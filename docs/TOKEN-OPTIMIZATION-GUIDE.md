# Optimizing AI Token/Credit Usage with the devops-os MCP Server

**Audience:** developers using Claude (or any MCP client) with the `devops-os` MCP server
**Why this exists:** every tool response here becomes part of the LLM's context — generated YAML, JSON bundles, and (since the suggestion-wiring fix) a prompt-analysis envelope all get read back into the conversation. Bigger/more responses cost more tokens per call, and extra conversational round-trips cost far more than any single large response. The suggestions below are grounded in this server's actual tested behavior, not generic advice.

---

## The single biggest lever: batch your requirements into one call

The most expensive pattern is iterative refinement — one tool call per requirement, each wrapped in a full assistant turn:

```
"Generate a GitHub Actions workflow for my Python app"
  -> "Now add Kubernetes deployment"
  -> "Now use kustomize instead of kubectl"
  -> "Now add a test matrix"
```

Each arrow is a full round trip: the model re-reads the entire conversation so far, re-generates a full response, and the previous tool output stays in context the whole time. The same outcome in one call:

```
"Generate a complete GitHub Actions workflow for a Python app, with Kubernetes
deployment via kustomize, and a version test matrix"
```
→ one tool call: `generate_github_actions_workflow(workflow_type="complete", kubernetes=True, k8s_method="kustomize", matrix=True, ...)`

This applies to every generator tool here — all 13 accept enough parameters to fully specify the output in one shot. Specify everything you know you need up front.

## Request only the scope you actually need

- **`workflow_type`/`pipeline_type`**: `"build"` alone is a fraction of the size of `"complete"` (which bundles build+test+deploy). If you're iterating on CI during development, use `"build"` and only switch to `"complete"` for the version you're actually committing.
- **`matrix=False`** (the default) unless you genuinely need multi-version test jobs — a matrix multiplies the generated YAML's job count.
- **`kubernetes=False`** (the default) unless you're actually deploying to K8s from that pipeline.
- **Version-management tools** (`get_version_config`, `check_version_updates`, `suggest_versions`, `check_security_issues`): pass a scoped `tools="python,go"` instead of leaving it empty. An empty string returns the *entire* tool database — every supported language/tool's version info — not just what you care about.

## Use multi-language parameters instead of one call per language

`generate_github_actions_workflow`, `scaffold_devcontainer`, and `generate_unittest_config` all accept a comma-separated `languages` list and produce **one** combined artifact. Prefer:

```
generate_github_actions_workflow(languages="python,go,java")
```
over three separate calls with `languages="python"`, `languages="go"`, `languages="java"` — three full tool-call round trips (and three full YAML outputs re-entering context) versus one. (We made exactly this mistake ourselves during this project's own MCP testing — five separate single-language calls where one multi-language call for most of them would have worked for the shared pipeline shape.)

## The prompt-suggestions feature is real now — know its token cost

Earlier in this project, the "prompt improvement suggestions" feature (analyzes how specific your prompt was, attaches follow-up suggestions) was silently dead in production due to a wiring bug. That's now fixed — which means **it actually adds tokens to every response where your prompt was vague**: the tool's raw output gets wrapped in a JSON envelope with `prompt_analysis` + `prompt_suggestions` + a summary, roughly 100–300 extra tokens per call.

This is a genuine trade-off, not a pure cost:
- **New to this server, or unsure what parameters exist?** Leave it on. One well-placed suggestion can save you an entire extra round-trip of guessing-then-correcting — which costs far more than the ~200 extra tokens.
- **Already know exactly what you want, calling this server repeatedly in a long session?** Turn it off — `DEVOPS_OS_ENABLE_SUGGESTIONS=false` (set before starting the server) — since a specific prompt rarely triggers suggestions anyway, but a slightly-vague one will now pay the tax on every single call.
- **Want suggestions but smaller:** `DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=1` and `DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS=false` keep the feature but shrink its payload.

The cheapest way to get the same benefit the suggestions provide, for free: **write a specific prompt in the first place** — name the language, cloud target, and deployment method. A specific prompt produces a high specificity score, which means no suggestions ever get attached, and you also skip the whole category of back-and-forth the suggestions exist to prevent.

## Don't ask the assistant to re-explain output it just generated

The tool's output (YAML, JSON bundle) is already in context once returned. Asking a follow-up like "explain what this workflow does" re-reads and re-narrates content that's already there — useful if you actually need the explanation, wasteful if you're just going to save the file. If you just need the artifact, say "write this to `.github/workflows/ci.yml`" rather than asking for both the artifact and a summary of it.

## Output is deterministic — don't regenerate across sessions

Every generator tool here produces byte-identical output for identical input (verified in `tests/test_scenario_based.py`'s determinism tests). If you've already generated an artifact once, save it — don't ask a fresh session to "generate the Kubernetes config for hello-go again" just to read it back. Re-running the exact same call costs the same tokens as the first time, for a result you already have on disk.

---

## If you only do one thing

Write one specific, fully-parameterized prompt per artifact instead of iterating. It's the only lever on this list that both shrinks the per-call payload *and* eliminates entire extra round trips — the two biggest costs on an MCP-heavy session.
