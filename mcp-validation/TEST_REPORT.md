# devops-os MCP Server — Test Report

**Date:** 2026-10-02
**Server:** `devops-os` (stdio, `.venv/bin/python -m mcp_server.server`), registered via project `.mcp.json`
**Tester role:** developer, scaffolding 5 "AI-era" language hello-worlds via MCP tools
**Status:** Bug #1 (workflow hang) fixed and verified. Bug #2 (prompt suggestions not surfaced) still open.

## Setup recap
`.venv` didn't exist on first connect (`ENOENT`). Created it (`python3 -m venv .venv`), installed `mcp_server/requirements.txt`, reconnected successfully. See prior session turns for detail.

## Test 1 — Hello-world scaffolding, 5 languages
Languages: Python, TypeScript, Go, Rust, Java (common "AI era" stack: ML/tooling in Python, web/agents in TS, infra/CLI in Go, performance-critical in Rust, enterprise in Java).

Bare-minimum source files created locally for each (not via MCP — MCP doesn't generate app code, only DevOps artifacts):
`hello/{python,typescript,go,rust,java}/...` — one entrypoint file each, minimal manifest where required (`package.json`, `go.mod`, `Cargo.toml`).

**Scaffold calls via `devops-os` tools:**

| Tool | Target | Result |
|---|---|---|
| `generate_k8s_config` | hello-go, generic | ✅ Success — Deployment+Service YAML, fast |
| `generate_k8s_config` | hello-go, specific (ns=production, replicas=3, port=8080) | ✅ Success — correctly reflected all params |
| `generate_github_actions_workflow` | hello-python | ❌ Hung >120s, backgrounded, no result |
| `generate_github_actions_workflow` | hello-typescript | ❌ `Connection closed` (parallel-call crash) |
| `generate_github_actions_workflow` | hello-go | ❌ Hung >120s, backgrounded, no result |
| `generate_github_actions_workflow` | hello-rust | ❌ `Connection closed` (parallel-call crash) |
| `generate_github_actions_workflow` | hello-java | ❌ Hung >120s, backgrounded, no result |
| `scaffold_devcontainer` | all 5 langs combined | ❌ `Connection closed` (parallel-call crash) |
| `generate_github_actions_workflow` | hello-python (retry, sequential, clean connection) | ❌ Hung >120s again — reproducible, not a concurrency artifact |

Artifacts saved: `hello/go/k8s/deployment-generic.yaml`, `hello/go/k8s/deployment-production.yaml`.

**4 of 5 language CI workflows could not be generated** — `generate_github_actions_workflow` is broken on this server instance. Root-caused and fixed below (see "Bug #1 — Fix & Verification").

## Bug #1 — Root cause, fix, and verification

**Root cause:** `generate_workflow()` in `devops_os/core/scaffold_gha.py` only dispatches on `workflow_type` ∈ `{build, test, deploy, complete, reusable}` (`WORKFLOW_TYPES`). The MCP tool's docstring in `mcp_server/server.py` falsely advertised `"basic"` as a valid value, and `validate_tool_inputs()` in `mcp_server/validators.py` never validated `workflow_type` at all. So `"basic"` sailed through into the generator's `else` branch:
```python
else:
    print(f"Error: Unknown workflow type '{args.type}'")
    sys.exit(1)
```
`sys.exit(1)` raises `SystemExit`, a `BaseException` not caught by normal exception handling. Inside the MCP server's async tool-call worker this silently killed the worker thread without ever sending a response back over stdio — the client-visible hang. Force-killing the pending call (`TaskStop`) left the stdio pipe broken, tearing down the entire server connection (all 13 tools), requiring a manual `/mcp` reconnect.

This fully explains every earlier observation: all `workflow_type="basic"` calls hung (5/5); the one call made without specifying `workflow_type` (defaults to `"complete"`) worked instantly; `generate_k8s_config` (unrelated code path) was unaffected throughout.

**Fix applied (3 changes):**
1. `mcp_server/validators.py` — added `workflow_type` validation via `validate_choice()` against the real 5 valid values, in the `generate_github_actions_workflow` branch of `validate_tool_inputs()`.
2. `mcp_server/server.py` — passed `workflow_type` into the `validate_tool_inputs()` call; corrected the docstring to list the real valid values instead of the fictional `"basic"`.
3. `devops_os/core/scaffold_gha.py` — replaced `sys.exit(1)` with `raise ValueError(...)` in `generate_workflow()`'s `else` branch, so even non-MCP callers (direct script use) fail loudly instead of hanging/killing the process. (The CLI's own `argparse` already restricts `--type` via `choices=WORKFLOW_TYPES`, so this only changes behavior for programmatic callers like the MCP server.)

**Verification:**

| Check | Result |
|---|---|
| Unit: `validate_tool_inputs(..., workflow_type="basic")` | ✅ Raises `ValidationError` instantly: `"workflow_type must be one of [...], got 'basic'"` |
| Unit: `scaffold_gha.generate_workflow()` with `type="basic"` | ✅ Raises `ValueError` instantly instead of `sys.exit(1)` |
| Live MCP: `generate_github_actions_workflow(workflow_type="basic")` | ✅ Instant error, no hang: `"Error executing tool ...: workflow_type must be one of [...], got 'basic'"` |
| Live MCP: all 5 languages with `workflow_type="build"` | ✅ All 5 succeeded instantly — Python, TypeScript, Go, Rust, Java workflows generated and saved to `hello/*/.github-workflow.yml` |
| Full pytest suite (`tests/` + `mcp_server/`) before vs. after fix | ✅ Identical: 382 passed, 2 skipped, same 5 pre-existing unrelated failures (`test_concurrency.py` — missing `pytest-asyncio` plugin in this venv, confirmed via `git stash` against unmodified `main`). No regressions. |

## Test 2 — Prompt-improvement suggestion feature
**Live MCP calls:** Called `generate_k8s_config` with a deliberately vague `user_context` ("deploy to kubernetes") and a rich, specific one. Neither call returned the documented suggestion envelope (`tool_output`/`prompt_analysis`/`prompt_suggestions`) — both returned raw tool output only, as if suggestions were disabled.

**Direct unit-level check** (bypassing the live server, same venv/code):
```
analyze_prompt('generate_github_actions_workflow', 'generate a cicd workflow')
→ specificity_score=0.0, gaps={missing_language, missing_cloud, missing_deployment, missing_testing: all True}
SuggestionEngine().generate_suggestions(...) → 2 high-confidence suggestions returned correctly
```
This confirms `prompt_analyzer.py` + `suggestion_engine.py` logic is correct in isolation, but **the live MCP tool responses never surface it** — `response_enhancer.py`'s enhanced JSON appears to get unwrapped back to plain `tool_output` somewhere between the tool handler and the MCP transport layer (config defaults are `enable_suggestions=true`, `confidence=medium`, so it should have fired).

**Verdict: prompt-improvement feature does not work end-to-end via the MCP server**, despite working correctly at the code-unit level. This is a wiring/serialization bug, not a design flaw.

## Reliability findings (unplanned, surfaced during testing)
1. **No concurrency support**: 8 parallel tool calls → 3 timed out, 4 failed with `Connection closed`, server disconnected entirely. The stdio server appears single-threaded/single-connection with no request queuing. **Status: not fixed** — out of scope for the Bug #1 fix, still a risk for any client issuing concurrent calls.
2. ~~`generate_github_actions_workflow` hangs deterministically~~ — **Fixed, see "Bug #1 — Root cause, fix, and verification" above.**
3. **Stopping a hung task kills the whole server connection** — a consequence of finding #2's root cause (`SystemExit` in a worker thread leaves stdio in a broken state). Should no longer occur now that `workflow_type` fails fast via `ValueError` instead of `sys.exit()`, but not independently stress-tested against other potential hang sources (e.g. finding #1's concurrency crash).

## Conclusion
- ✅ Hello-world scaffolds created for all 5 languages (locally, since MCP doesn't generate app code).
- ✅ Kubernetes manifest generation works correctly and respects all input parameters.
- ✅ **GitHub Actions workflow generation — fixed.** All 5 languages now generate successfully via the live MCP server with no hang.
- ❌ Dev container scaffolding still untested cleanly (only attempted under the concurrency-crash scenario; not retried).
- ❌ Prompt-improvement suggestions still do not reach the client despite correct underlying logic — **open defect**, worth filing upstream (`cloudengine-labs/devops_os`), referencing `mcp_server/response_enhancer.py`. Not addressed in this pass.
- ⚠️ Server still has no tolerance for concurrent calls (finding #1) — recommend sequential usage until that's addressed separately.

## Artifacts
```
hello/
├── python/{app.py,.github-workflow.yml}
├── typescript/{index.ts,package.json,.github-workflow.yml}
├── go/{main.go,go.mod,.github-workflow.yml,k8s/deployment-generic.yaml,k8s/deployment-production.yaml}
├── rust/{main.rs,Cargo.toml,.github-workflow.yml}
└── java/{Hello.java,.github-workflow.yml}
TEST_REPORT.md   (this file)
```

## Code changes (fix for Bug #1)
```
mcp_server/validators.py        — validate workflow_type against real valid choices
mcp_server/server.py            — pass workflow_type into validation; fix stale docstring
devops_os/core/scaffold_gha.py  — raise ValueError instead of sys.exit(1) on unknown type
```
Unstaged in git as of this report. Not yet committed.
