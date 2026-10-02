---
title: "A Real-Time MCP Dev Session: Scaffolding, Breaking, and Fixing DevOps-OS's MCP Server"
slug: "realtime-mcp-debugging-devops-os-mcp-server"
description: "A live walkthrough of using DevOps-OS's MCP server to scaffold projects in 5 languages, hitting a real hang bug, root-causing it with git archaeology, and shipping the fix."
topic: "ai-devops"
tags: ["MCPServer", "DevOpsOS", "Debugging", "AIAgents", "ClaudeCode", "RootCauseAnalysis"]
publishedAt: "2026-10-02"
featured: false
---

# A Real-Time MCP Dev Session: Scaffolding, Breaking, and Fixing DevOps-OS's MCP Server

Most MCP write-ups show the happy path: connect the server, ask for a workflow, get YAML back. This post is the opposite — a real debugging session where the happy path broke, and what it took to find out why.

The goal was simple: act like a developer scaffolding bare-minimum "hello world" projects in five languages — Python, TypeScript, Go, Rust, Java — and use DevOps-OS's MCP server to generate the CI/CD and Kubernetes config for each. Along the way, one of the MCP tools hung for over two minutes and took the whole server connection down with it. Here's the full trace, from symptom to root cause to fix.

## Setting up

The server was already wired up via `.mcp.json`, but the Python virtual environment it pointed to didn't exist yet:

```
ENOENT: no such file or directory, posix_spawn '.venv/bin/python'
```

A one-time fix:

```bash
python3 -m venv .venv
.venv/bin/pip install -r mcp_server/requirements.txt
```

Reconnect, and `devops-os` shows up with 12 tools: GitHub Actions, Jenkins, GitLab CI, Kubernetes manifests, ArgoCD/Flux, SRE configs, dev containers, and version-management helpers.

## The first crack: concurrency

Scaffolding 5 languages plus a shared dev container plus a couple of prompt-quality tests meant 8 tool calls. Sent in parallel, to save time:

```
MCP tool "devops-os/generate_github_actions_workflow" is still running after 120s...
error: Connection closed
error: Connection closed
error: Connection closed
```

Three calls timed out, four died outright, and the server disconnected entirely. Lesson one, immediately: **this stdio MCP server has no concurrency tolerance.** One request at a time, or it falls over.

## The real bug: one call, still hanging

Retrying sequentially — one call, on a fresh connection — `generate_github_actions_workflow` still hung. Not a concurrency artifact. Something about this one call was broken.

The only variable that stood out: every failing call used `workflow_type="basic"`. The one call that had worked earlier in the session never set `workflow_type` at all — it used the default, `"complete"`.

Reproducing the exact server code path directly, with a `faulthandler` watchdog so a hang would dump a stack trace instead of sitting forever:

```python
import faulthandler
faulthandler.dump_traceback_later(8, exit=True)

from devops_os.core import scaffold_gha
# ... build the same args the MCP tool builds ...
scaffold_gha.generate_workflow(args, {}, configs)
```

Instead of hanging, it printed:

```
Error: Unknown workflow type 'basic'
```

...and exited. That was the whole story, hiding in plain sight.

## Root cause

```python
# devops_os/core/scaffold_gha.py
WORKFLOW_TYPES = ["build", "test", "deploy", "complete", "reusable"]

def generate_workflow(args, values, configs):
    if args.type == "build":
        return generate_build_workflow(args, values, configs)
    # ... test, deploy, complete, reusable ...
    else:
        print(f"Error: Unknown workflow type '{args.type}'")
        sys.exit(1)
```

`"basic"` was never a supported value — not now, not at any point in 287 commits of history (we checked). But the MCP tool's own docstring in `mcp_server/server.py` claimed:

```python
"""
workflow_type: 'basic' or 'complete' (default: 'complete')
"""
```

And `mcp_server/validators.py`'s `validate_tool_inputs()` validated `name` and `languages` for this tool — but never `workflow_type`. So the bad value sailed straight through into that `else` branch.

The real damage came from `sys.exit(1)`. It raises `SystemExit`, which ordinary `except Exception` handling doesn't catch. Inside the MCP server's async tool-call worker, that silently killed the worker thread — no response, no exception, ever sent back over stdio. The client just waits. Force-cancelling the stuck call left the stdio pipe broken, taking the entire connection down, not just that one request.

**The docstring was simply wrong**, introduced in an earlier commit that added docstrings and input validators across all 8 tools in one pass — without cross-checking this one parameter against the enum it actually dispatches on, two files away in the same diff.

## The fix

Three small, targeted changes:

**1. Validate the real values** (`mcp_server/validators.py`):
```python
if "workflow_type" in validated:
    validated["workflow_type"] = validate_choice(
        validated["workflow_type"],
        ["build", "test", "deploy", "complete", "reusable"],
        "workflow_type",
    )
```

**2. Wire it in and fix the docstring** (`mcp_server/server.py`):
```python
validate_tool_inputs(
    "generate_github_actions_workflow",
    name=name, languages=languages, workflow_type=workflow_type,
)
```

**3. Never let library code call `sys.exit()`** (`devops_os/core/scaffold_gha.py`):
```python
else:
    raise ValueError(
        f"Unknown workflow type '{args.type}'. Valid types: {WORKFLOW_TYPES}"
    )
```

The CLI's own `argparse` already restricts `--type` via `choices=WORKFLOW_TYPES`, so this only changes behavior for programmatic callers like the MCP server — exactly where it was silently fatal before.

## Verifying it

Before fix, calling with `"basic"`:
```
MCP tool "devops-os/generate_github_actions_workflow" is still running after 120s.
```

After fix, same call:
```
Error executing tool generate_github_actions_workflow:
workflow_type must be one of ['build', 'test', 'deploy', 'complete', 'reusable'], got 'basic'
```

Instant, instead of a two-minute hang. Then the actual goal — real workflows for all five languages, sequentially, with a valid `workflow_type`:

```
hello-python   ✅
hello-typescript ✅
hello-go       ✅
hello-rust     ✅
hello-java     ✅
```

And the full pytest suite, before and after the change: **382 passed, 2 skipped**, identical in both runs (confirmed via `git stash` against unmodified `main`) — no regressions.

## What this was actually about

The interesting part wasn't the bug itself — a mismatched docstring is an easy mistake. It's what made it dangerous: an *unvalidated* claim met a function that *terminates the process* instead of raising. Either one alone is a minor issue. Together, they turned "wrong default" into "silently kill the server."

If you're exposing existing library/CLI code as MCP tools, two checks are worth doing on every wrapper:
- Does every documented parameter value actually exist in the code it dispatches to?
- Does any code in that call path call `sys.exit()`, `os._exit()`, or anything else that terminates a process rather than raising? If it's reachable from a server, that's a hang (or worse) waiting to happen.

The full before/after artifacts — five hello-world scaffolds, the generated CI workflows, and the complete test trace — live in [`mcp-validation/`](../mcp-validation/) in this repo.
