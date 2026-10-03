---
title: "DevOps OS MCP Server Development Journey with AI Coding Agents"
slug: "mcp-server-development-journey-ai-coding-agents"
description: "Building and hardening DevOps-OS's MCP server end to end with AI coding agents — GitHub Copilot's agent mode for the initial build, a Claude Code session for the testing and bug-fixing pass — the test approach, the dev process, and the prompting techniques that actually worked."
topic: "ai-devops"
tags: ["AIAgents", "MCPServer", "GitHubCopilot", "ClaudeCode", "DevOpsOS", "Testing"]
publishedAt: "2026-10-03"
featured: true
---

# MCP Server Development Journey with AI Coding Agents

I built DevOps-OS's MCP server almost entirely with AI coding agents — not as an experiment, but because that's genuinely how I build things now. Different stages of the work called for different tools: GitHub Copilot's agent mode did the initial construction fast and mostly hands-off, and later a dedicated Claude Code session did the part construction doesn't cover — actually using the thing, finding what it got wrong, and fixing it. This post is that whole journey, not a story about switching allegiances between tools.

GitHub Copilot's agent mode wrote the bulk of the server — input validation, docstrings, 13 tool wrappers around the existing CLI generators. It worked. I connected it to Claude Code, asked it to generate a few configs, got real YAML back, moved on.

Then, in a separate session, I spent real time with Claude Code actually trying to *use* the thing — scaffolding real projects, testing edge cases, acting as a test architect instead of a happy-path user — and found four real bugs, one of which was a production healthcheck that had been silently broken the whole time. This post covers what the server does, what each AI agent actually contributed at its stage, the testing approach that surfaced the problems, and the prompting techniques I'm taking away from the whole thing.

## What DevOps-OS's MCP server actually is

DevOps-OS is a CLI that scaffolds DevOps artifacts — GitHub Actions workflows, Jenkins pipelines, Kubernetes manifests, ArgoCD/Flux configs, SRE/observability configs, dev containers. The MCP server is a thin protocol adapter over the same generator functions: ask Claude (or any MCP client) in plain English, get back production-shaped YAML. 13 tools, one server, `python -m mcp_server.server` over stdio for local use.

The idea is sound and the generators themselves are solid — hundreds of existing unit tests covered the actual YAML-generation logic well. The part that broke was the *seam*: the thin layer connecting the tools to the MCP protocol, and the validation that was supposed to guard it.

## Building it: GitHub Copilot's agent mode

GitHub Copilot's agent mode (I had it running on a Claude Haiku model) did the actual construction work: wrapping each CLI generator as an `@mcp.tool()` function, adding input validators, writing docstrings, even running its own baseline audit of the implementation before diving in. That audit is worth pausing on, because it's the single most interesting artifact from this whole project.

The agent's own pre-work audit explicitly listed, as a known gap:
> 7. No timeout enforcement (potential hang)

It named the exact failure mode that shipped one commit later. The very next commit added a docstring claiming a parameter (`workflow_type`) accepted a value — `"basic"` — that had never existed in the underlying generator, at any point in the project's history. No validator caught it. That unvalidated value eventually reached a `sys.exit(1)` deep in the generator, which — called from inside a live server's worker thread — doesn't exit cleanly. It just hangs, forever, and takes the connection down with it.

The agent had the right instinct and the wrong follow-through: it correctly predicted the risk, then didn't check its own next commit against it.

## Testing it: a dedicated Claude Code session

A separate Claude Code session covered the part Copilot's agent mode hadn't: using the server like a real developer would, in a session built for iterative debugging rather than one-shot generation. The first thing I asked for was simple — scaffold hello-world projects in five languages (Python, TypeScript, Go, Rust, Java) using the MCP tools. That's where `workflow_type="basic"` first hung the server, and where the actual debugging work started.

## The testing approach: acting as a test architect, not a user

The habit that found the most bugs wasn't clever debugging — it was a fixed scenario framework applied to every tool, the same shape every time, so a missing category is visible by omission:

| Category | What it checks |
|---|---|
| Happy path | Realistic input works |
| Boundary | Exact edges of every numeric/length limit |
| Invalid/rejected | The validator actually rejects what it claims to |
| Cross-parameter | Flag combinations that interact |
| Adversarial | Shell metacharacters, malformed JSON, injection |
| Live-protocol | Does the *real* server — not just the function — behave correctly |
| Determinism | Same input twice, same output |

That last two rows mattered more than I expected. Most of the project's existing tests called tool functions directly in Python — fast, but they bypass the actual server's startup wiring entirely. A whole category of bug (the prompt-suggestion feature, dead since it was built) was invisible to every one of those unit tests and only showed up once I spawned the real server as a subprocess and spoke actual MCP wire protocol to it. "Does this work" and "does this work *through the server a real client would hit*" turned out to be different questions with different answers.

Running that framework against all 13 tools surfaced a new bug the unit-test suite had missed entirely: `generate_argocd_config`'s `repo` and `image` parameters were never validated at all, despite a validator existing in the code for both — just never wired to the call site. Same root pattern as the `workflow_type` bug: logic written, never connected.

## The bug trail

In rough order of discovery:

1. **`workflow_type="basic"` hangs the server.** `sys.exit(1)` inside a worker thread, no timeout, no clean error. [Full root-cause writeup here.](./2026-10-02-realtime-mcp-debugging-devops-os-mcp-server.md)
2. **Prompt-improvement suggestions were dead in production.** The function that initializes the suggestion engine was simply never called on the path the real server actually runs. Found with zero live calls — three `grep`s, reasoning backward from one known symptom.
3. **ArgoCD's `repo`/`image` validation was dead code.** Found by the scenario-matrix pass, not by reading code.
4. **Jenkins/GitLab pipeline types had no validation**, Jenkins/GitLab's own generators just silently produce an incomplete pipeline on a bad value instead of hanging — lower severity, same category.
5. **`ConcurrencyManager` was unit-tested and never invoked anywhere in the real request path.** Wired it in properly — then scientifically disproved my own assumption that this was *the* fix for the original crash. Stashing the change and re-running the same 25-call reproduction against the old code gave identical results. The original crash was almost certainly the `workflow_type` hang hitting several calls at once, not a distinct concurrency defect. Worth shipping anyway as real defense-in-depth; not worth claiming credit for fixing something it didn't.
6. **`/health` and `/ready` didn't exist as routes at all** — and `docker-compose.yml`'s own healthcheck, plus the project's smoke-test script, had been calling `GET /health` and silently failing the whole time. Found by asking "why are these 4 tests skipped" and not accepting "they test something that doesn't exist" as a good enough answer.
7. **Two SDK-client tests had never run, ever.** The import named `StdioClientTransport` — the MCP *TypeScript* SDK's class name, never valid in the Python SDK. Fixed the import, then replaced two vacuous assertions (`ClientSession is not None`) with tests that actually drive the server through the real client library.
8. **`pytest-asyncio` was never installed.** Every `@pytest.mark.asyncio` test in the suite had been silently not-executing. CI had already discovered this and quietly worked around it with a `-k "not asyncio"` filter instead of fixing it.

Final state: 485 tests, all passing, zero skipped — up from 479 passing / 4 skipped (where two of those four had, in effect, *never actually run*, not just been excluded).

## Prompting techniques that actually mattered

**Ground claims in the source, not in plausibility.** The whole bug chain traces back to a docstring describing a parameter's valid values from inference rather than from reading the enum it dispatched to. The fix as a standing practice: when an agent documents a constraint, make it quote the actual code it's constraining, not infer something that sounds right.

**One source of truth, enforced structurally.** A validator and a docstring describing the same constraint in two places will eventually disagree. Import the real constant into the validator instead of retyping it.

**Demand a per-item checklist, not a summary sentence.** "Added validation to all 8 tools" is unfalsifiable at a glance. "Here's a table: tool × parameter × validated-against-what" is checkable in the diff.

**A test for every claim.** If a docstring says a parameter accepts X, there should be a test that passes something outside X and asserts rejection. The `workflow_type` bug shipped without one; I caught myself shipping its *fix* the same way before writing the regression test.

**Library code must never call `sys.exit()`.** That line is only safe at an actual CLI's `if __name__ == "__main__":` boundary. Anywhere reachable from a server or worker thread, it's a hang waiting to happen — this is the single highest-leverage code-review heuristic that came out of this whole project.

**Verify before claiming, especially against your own hypothesis.** The concurrency fix would've been easy to ship as "fixed the crash." Stashing it and re-testing against the unmodified code — and reporting honestly that it didn't reproduce the original failure either way — mattered more than the fix itself.

**Batch requirements into one request.** Asking for a workflow, then kubernetes, then a test matrix, as three separate asks costs three full round-trips of re-read context plus three full tool outputs re-entering context. One fully-specified ask costs one.

**Don't bundle unrelated asks into one message.** "Fix these four bugs, also here's a separate question about token economics" risks the second half getting less attention than it would on its own. I've since added this as a standing rule in my own CLAUDE.md.

## What I'd tell someone starting the same way

Using an agentic coding tool to build the first version fast, then a separate, deliberate testing pass with a different tool (or at least a different mode — deep investigation instead of one-shot generation) to actually exercise it, is a reasonable division of labor. The mistake is skipping the second half because the first half compiled and returned something that looked right. Three of the four bugs that shipped were never caught by "does it return valid YAML" — they were only caught by "what happens when the input is wrong," "does this run through the real server," and "why is this test not actually testing anything." None of those questions are expensive to ask. They're just easy to skip when the happy path already works.

Full technical detail on the test strategy lives in [`docs/mcp/MCP-TEST-STRATEGY.md`](../docs/mcp/MCP-TEST-STRATEGY.md), the incident log in [`mcp-validation/TEST_REPORT.md`](../mcp-validation/TEST_REPORT.md), and the deep dive on the first bug in [the previous post](./2026-10-02-realtime-mcp-debugging-devops-os-mcp-server.md).
