---
title: "What a Week Debugging an AI-Agent-Written MCP Server Actually Taught Us"
slug: "lessons-debugging-ai-agent-mcp-server"
description: "Two real production bugs, a 230-test suite audit, and a trail back to an AI coding agent's own ignored risk audit — lessons for teams building with agentic coding tools."
topic: "ai-devops"
tags: ["AIAgents", "MCPServer", "Testing", "DevOpsOS", "ClaudeCode", "CodeReview"]
publishedAt: "2026-10-03"
featured: false
---

# What a Week Debugging an AI-Agent-Written MCP Server Actually Taught Us

[A previous post](./2026-10-02-realtime-mcp-debugging-devops-os-mcp-server.md) walked through the mechanics of one bug in DevOps-OS's MCP server: a tool hung for two minutes because a docstring advertised a parameter value that didn't exist. This post is about what came after — a second bug found with zero live calls, a full test-suite audit, and a surprising answer to "whose fault was this, really?"

## Bug #2: found without touching the server

After fixing the hang, the obvious next question was whether DevOps-OS's "prompt improvement suggestions" feature — a system that analyzes how vague your request was and suggests better wording — actually worked. Live testing earlier had shown it silently never fired, for any prompt, ever.

Rather than poke at the live server again, the fix came from three greps:

```python
# mcp_server/server.py, line ~227
mcp = FastMCP("devops-os", ...)   # module-level instance, tools decorated onto it directly

# __main__ block, stdio branch:
if config.transport == "stdio":
    mcp.run(transport="stdio")    # <- runs the module-level instance directly
```

`create_mcp_server()` — the *only* function that initializes `_response_enhancer` and `_concurrency_manager` — was never called on the stdio path. It builds a second, separate `FastMCP` instance that nobody actually runs. Every tool handler's call to `get_response_enhancer()` raised `RuntimeError`, silently caught, falling back to raw output. Every single time, for the entire life of the server.

The fix was three lines: initialize those globals directly in `__main__` before `mcp.run()`, without touching the FastMCP instance architecture. Verified by simulating the exact startup state and confirming the same vague prompt that used to return bare YAML now returned the full suggestion envelope. No live MCP round-trip needed until the very end, for a final sanity check.

**The lesson:** not every bug needs a live reproduction loop. Once you have one confirmed symptom and a hypothesis, `grep` for where the two code paths diverge is often faster than another round of tool calls — especially when every live round trip costs a client timeout cycle.

## The fix exposed something else: brittle tests

Fixing Bug #2 correctly made two existing tests fail:

```python
def test_call_generate_argocd_config(self):
    text = self._call_tool("generate_argocd_config", {...})
    data = json.loads(text)
    assert "argocd/application.yaml" in data   # now fails — see below
```

These tests spawn the *real* server as a subprocess and talk real MCP protocol to it — the most rigorous test in the suite. They broke because they assumed the top-level JSON response was always the raw tool bundle. Once suggestions started actually firing (correctly, finally), the top level became the suggestion envelope, with the real bundle nested under `tool_output`.

These tests had been quietly encoding the bug as "correct behavior." They only ever passed because the feature they didn't know about was dead. Fixing them meant writing a small unwrap helper and teaching four tests to look for the bundle whether or not it's wrapped — which is what a real MCP client has to do anyway.

**The lesson:** a passing test suite after a bug fix doesn't just mean "no regressions." Sometimes it means some of your tests were quietly asserting the *bug* as the expected behavior, and you won't find out until you fix the thing they were built against.

## Auditing all 230 tests for "good and bad scenarios"

With two real bugs behind us, the natural next question was: would the test suite have caught either one? A full pass through all nine test files turned up a consistent shape:

**What's done well.** The hardening-policy tests (`test_hardening_scaffold.py`) and the input validators (`test_config.py`) follow a disciplined pattern — nearly every accepted case has a matching rejected case:
```python
def test_kyverno_type_accepts_asvs_l1(self): ...
def test_inspec_type_rejects_asvs_l1(self): ...
```
That pairing is the whole game. It's what lets a reviewer (human or AI) scan a diff and immediately see what's *not* tested, because the pattern itself tells you what's missing.

**What isn't.** Three specific gaps, each one tied to something that actually broke:

1. **The exact parameter from Bug #1 (`workflow_type`) has no test, including the fix.** `test_validate_github_actions_workflow` checks `name`, never `workflow_type`. I added real validation for it and shipped the fix without writing the test that would catch someone reverting it. Caught this by literally applying my own rule from the first debugging session — "write a test for every claim" — against my own patch, after the fact.
2. **Bug #2 has no regression guard.** The one test file that runs the real subprocess never checks for the suggestion envelope. Revert the `__main__` fix tomorrow, and the full suite stays green.
3. **A feature's tests pass while the feature runs nowhere.** `ConcurrencyManager` has solid unit tests — and is never called from any tool handler. `grep "get_concurrency_manager"` turns up its own definition and nothing else. Those tests verify the component works in isolation; they say nothing about whether a live server is protected, which is exactly why eight parallel calls crashed it earlier in this project.

And one that isn't a gap so much as a false signal:

```python
def test_health_endpoint_format(self):
    """Test that /health endpoint would return proper JSON."""
    # We mock the response since we can't start a live server in tests
    expected_response = {"status": "alive", ...}
    assert expected_response["status"] == "alive"   # asserts itself
```
This test — and a few siblings — construct the expected answer by hand and then check it against itself. It cannot fail. It also cannot tell you anything about the real `/health` endpoint.

**The lesson:** "382 passed" is not the same claim as "382 tests would catch a regression." A suite needs auditing the same way code does — not just for coverage percentage, but for whether each test is actually exercising the real path, and whether accept/reject cases come in pairs.

## Whose bug was this, actually?

The `workflow_type` docstring bug was authored by an AI coding agent — GitHub Copilot's agent mode, running (per the person who ran it) on a Claude Haiku model — in a commit that also claimed "Integrate validators into all 8 tools." Before blaming the model, we checked the repo's own history for a cheap, obvious explanation: maybe `"basic"` used to be a real CLI option, and migrating the code into an MCP wrapper just lost track of it.

A full search of 287 commits found no trace of `"basic"` ever being valid, anywhere. But it found something more specific: a baseline-audit commit from the *same agent session*, written one commit earlier, that explicitly listed:

> 7. No timeout enforcement (potential hang)

as a known gap. The agent had correctly named the exact failure mode that was about to ship — then, one commit later, closed out "add validation" without checking the new work against the risk it had just written down itself.

**The lesson for teams using agentic coding tools:** the fix isn't "don't trust the agent" — it's narrower than that. Require claims to cite their source ("quote the actual enum, don't infer plausible values"), make completeness claims falsifiable ("show a per-tool, per-parameter table, not a summary sentence"), and — this is the one that's easy to miss — check new work against the agent's *own* prior findings, not just against the task description. The information to prevent this bug already existed in the repository. It just wasn't used as a checklist.

## The short version

- A hang bug and a silently-dead feature both came from the same root pattern: a claim (a docstring, a "fully validated" commit message) that was never checked against the code it described.
- Fixing the second bug took three greps and zero live server calls, once there was a clear symptom to reason backward from.
- Fixing a bug can retroactively reveal that some passing tests were testing the bug, not the feature.
- A test suite's pass rate tells you less than its *shape* — whether rejections are paired with acceptances, and whether the thing under test is actually wired into the live path.
- When an AI agent ships a bug, the most useful question usually isn't "was the model bad" — it's "did the process check the agent's own claims against the source, and against its own earlier findings." Here, it didn't, twice.

The full trace — commits, error messages, before/after test runs — is in [`mcp-validation/TEST_REPORT.md`](../mcp-validation/TEST_REPORT.md) in this repo.
