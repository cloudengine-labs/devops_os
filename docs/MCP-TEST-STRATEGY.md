# MCP Server — Scenario-Based Test Strategy

**Date:** 2026-10-03
**Scope:** all 13 tools exposed by the `devops-os` MCP server (`mcp_server/server.py`)
**Test suite:** `tests/test_scenario_based.py` (84 tests), building on the existing `tests/` + `mcp_server/test_*.py` suite (382 tests)
**Related:** [`mcp-validation/TEST_REPORT.md`](../mcp-validation/TEST_REPORT.md) (the incident log — how 3 of these bugs were actually found and fixed), `tests/test_mcp_protocol.py` (live wire-protocol tests this strategy reuses)

---

## Why this document exists

The existing suite (382 tests before this pass) is heavy on "does valid input produce valid output" and much lighter on "does invalid input get rejected, and does this actually run in the deployed server." That asymmetry is exactly what let two real bugs ship silently (documented in `mcp-validation/TEST_REPORT.md`). This document is the general, reusable strategy — not an incident report — for closing that gap across every tool, and for keeping it closed as new tools are added.

---

## The scenario framework

Every tool is run through the same fixed shape. The shape itself is the point: if a tool is missing a row, that's visible by omission, not by having to remember to think of it.

| Category | Question it answers | What it has caught |
|---|---|---|
| **Happy path** | Does realistic input work? | Baseline only — passes even when a tool is badly broken elsewhere |
| **Boundary** | What happens exactly at and past every numeric/length limit? | `replicas=101`, `port=65536`, `slo_target=49.99` |
| **Invalid / rejected** | Does the validator actually reject what it claims to reject? | The exact class of bug behind the `workflow_type="basic"` hang |
| **Cross-parameter** | Do flag combinations that change behavior together still behave correctly? | `kubernetes=True` × each `k8s_method`; `auto_sync` + `rollouts` together |
| **Adversarial / structural** | Shell metacharacters, malformed JSON, unknown enum values, empty/huge strings | `generate_argocd_config`'s `image`/`repo` injection gap (Bug #3) |
| **Live-protocol** | Does the *real* subprocess server (not just the Python function) behave correctly? | Bug #2 — suggestions worked in isolation, never fired through the real stdio entrypoint |
| **Determinism** | Same input twice → identical output? | Matters for GitOps diffing / CI reproducibility; not yet violated, but untested before this pass |

### Why two different calling styles are both necessary

Most scenario tests call the tool's Python function directly (`generate_k8s_config(...)`) — fast, lets you run hundreds of parameter combinations in milliseconds. But this bypasses `mcp_server/server.py`'s module-level `mcp` vs. `create_mcp_server()` split entirely: `_response_enhancer` and `_concurrency_manager` are only ever `None` or real depending on *which* code path actually ran, and a unit-level call can't see that difference. Bug #2 was invisible to every unit-level test in the suite — it only showed up in `test_mcp_protocol.py`, the one file that spawns `python -m mcp_server.server` as a real subprocess and talks actual MCP JSON-RPC to it.

**Rule applied here:** any claim about behavior that depends on server *wiring* (suggestions, concurrency limits, auth) needs at least one live-protocol test via `_MCPSession` (reused from `test_mcp_protocol.py`), not just a unit-level call. Everything else — pure input validation, generator output shape — is fine at the unit level and should stay there for speed.

### Why the hello-world sample apps

Scenarios use the project's own 5 sample apps (`hello-python`, `hello-typescript`, `hello-go`, `hello-rust`, `hello-java`, created during the earlier MCP validation pass) as realistic input instead of synthetic placeholder strings like `"my-app"`. This keeps the test suite's "happy path" grounded in something a reader can cross-reference against real generated output in `mcp-validation/hello/`, rather than abstract fixtures that only exist inside the test file.

---

## Coverage by tool

| Tool | Happy | Boundary | Invalid/rejected | Cross-param | Adversarial | Determinism | Finding |
|---|---|---|---|---|---|---|---|
| `generate_github_actions_workflow` | ✅ | ✅ (languages) | ✅ (`workflow_type`) | ✅ (k8s methods) | ✅ (name injection) | ✅ | Bug #1 fixed; now the only tool with a direct regression test for it |
| `generate_jenkins_pipeline` | ✅ | — | — | — | ✅ (name injection) | — | **Gap found**: `pipeline_type` has no validator at all (asymmetric with GHA) — documented, not yet fixed, pending a decision |
| `generate_gitlab_ci_pipeline` | ✅ | — | — | — | — | — | Same `pipeline_type` gap as Jenkins |
| `generate_k8s_config` | ✅ | ✅ (replicas, port, both edges) | ✅ (image injection) | ✅ (expose_service, deployment_method ×4) | ✅ | ✅ | Confirmed correctly defended at every edge |
| `generate_argocd_config` | ✅ | ✅ (repo length) | ✅ | ✅ (auto_sync + rollouts) | ✅ (image injection) | — | **Bug #3 found and fixed**: `repo`/`image` were never passed into validation at all |
| `generate_sre_configs` | ✅ | ✅ (slo_target, both edges) | ✅ | ✅ (all 4 slo_types) | — | — | Confirmed correct |
| `scaffold_devcontainer` | ✅ (all 5 langs) | ✅ (empty languages) | ✅ (mixed valid+invalid list) | — | — | — | Confirmed fail-closed (rejects whole list, doesn't silently drop the bad entry) |
| `generate_unittest_config` | ✅ | — | ✅ | — | — | — | Confirmed the `name`→`project_name` validator rename is intentional, not a bug (looked like one during review) |
| `get_version_config` / `check_version_updates` / `suggest_versions` / `check_security_issues` | ✅ | — | ✅ (unknown tool) | — | — | — | Confirmed graceful error envelope, no crash |
| `update_versions` | ✅ | — | ✅ (malformed JSON, empty object) | — | ✅ (unknown tool + bogus version) | — | Confirmed `VersionManager.set_version`'s whitelist already correctly rejects both, and never touches `os.environ` on rejection — the one tool that was well-defended going in |

---

## What this pass found

Three bugs, all the same root pattern: **validation logic existed in `validators.py`, was never wired to the parameter it was written for.**

| Bug | Tool | Gap | Fix |
|---|---|---|---|
| #1 | `generate_github_actions_workflow` | `workflow_type` never validated; `"basic"` (a value that never existed) reached `sys.exit(1)` in a server worker thread, hanging the whole connection | Added `validate_choice()`, replaced `sys.exit(1)` with `raise ValueError` |
| #2 | All tools (server-wide) | `create_mcp_server()` — the only function that initializes `_response_enhancer`/`_concurrency_manager` — was never called on the stdio path; suggestions silently never fired in production | Initialize those globals directly in `__main__` before `mcp.run()` |
| #3 | `generate_argocd_config` | `repo`/`image` never passed into `validate_tool_inputs()`, despite validators existing for both; `image="...$(whoami):latest"` was silently accepted | Pass `repo=repo, image=image` into the validation call |

None of these were found by reading code in isolation — all three were found by designing the scenario *first* ("what should happen if `workflow_type` is invalid?", "what should happen if `image` contains shell metacharacters?") and then checking whether the code actually did that, rather than reading the code and assuming the docstring or the existence of a validator function meant it was wired up.

## Known gaps not fixed in this pass

- **Jenkins/GitLab `pipeline_type` has no validation**, unlike GHA's `workflow_type`. Doesn't hang (no `sys.exit()` in that path), but accepts any string silently — a decision is needed on whether to match GHA's strictness or leave it permissive.
- **`ConcurrencyManager` is unit-tested but never invoked** from any tool handler (`grep get_concurrency_manager` only finds its own definition) — its tests pass while providing zero actual protection, which is why parallel calls crashed the server during earlier testing. Not a scenario-test gap so much as a dead-code gap; needs a product fix (wire it into the tool-call path), not a test.
- **HTTP transport (`sse`/`streamable-http`) has the identical Bug #2 pattern** — its branch in `__main__` also never calls `create_mcp_server()`. Not fixed here because stdio is what's actually deployed via `.mcp.json`; flagged for the same fix if HTTP is ever used in production.
- **Several `mcp_server/test_http.py` tests are tautological** (assert a hand-built dict against itself, e.g. `test_health_endpoint_format`) — they can't fail and don't test the real endpoint. Not touched in this pass; would need an actual live HTTP server fixture to test for real.

---

## How to extend this suite

When adding a new MCP tool:
1. Add a row to the coverage table above before writing code — decide up front which categories apply (not every tool needs cross-parameter tests; every tool needs invalid/rejected if it has any validated field).
2. Write the validator in `validators.py` **and** the test in the same change — Bug #1's postmortem rule ("write a test for every claim") applies literally: a validator with no corresponding rejection test is exactly how Bugs #1 and #3 shipped.
3. If the new behavior depends on server-level wiring (not just input validation), add at least one `_MCPSession`-based live test, not just a unit-level call — Bug #2 is the reason this rule exists.
4. Reuse the hello-world sample apps (`mcp-validation/hello/`) for happy-path input where an app name/image is needed, instead of inventing a new placeholder each time.
