"""
MCP Wire-Protocol Tests for DevOps-OS MCP Server.

What these tests prove
----------------------
These tests exercise the *actual MCP JSON-RPC 2.0 wire protocol* by spawning
``python -m mcp_server.server`` as a real subprocess and communicating with it
over stdin/stdout — exactly the same channel that Claude Code, Cursor, VS Code
Copilot, or any other MCP client uses.

They prove:
  1. **Handshake** — the server completes the MCP initialize / notifications/initialized
     exchange and returns the correct ``protocolVersion`` and ``serverInfo``.
  2. **Tool discovery** — ``tools/list`` returns all eight expected DevOps-OS tools
     with their names and descriptions intact.
  3. **Tool invocation** — ``tools/call`` for representative tools (GHA, Jenkins,
     Kubernetes, SRE, ArgoCD, GitLab, devcontainer, unittest) returns a non-empty
     text response that contains expected artifact content (YAML/JSON/Groovy
     keywords).
  4. **Error handling** — calling a tool that does not exist returns a JSON-RPC
     error response (not a crash or hang).
  5. **Sequential calls** — the server handles multiple back-to-back ``tools/call``
     requests without restarting, proving stateless-but-persistent request handling.

No Claude CLI, no API key, and no network access are required.  The server
communicates over stdio (the MCP stdio transport), so every test runs in any
CI environment that has Python 3.10+.
"""

import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional
# ---------------------------------------------------------------------------
# Expected tool names (all 8 DevOps-OS tools exposed by the MCP server)
# ---------------------------------------------------------------------------

EXPECTED_TOOLS = {
    "generate_github_actions_workflow",
    "generate_gitlab_ci_pipeline",
    "generate_jenkins_pipeline",
    "generate_k8s_config",
    "generate_argocd_config",
    "generate_sre_configs",
    "scaffold_devcontainer",
    "generate_unittest_config",
}

# Root of the repository (one level above this tests/ directory)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Helper: thin MCP session over a subprocess
# ---------------------------------------------------------------------------

class _MCPSession:
    """
    Manages a single MCP stdio session with ``mcp_server.server``.

    Usage::

        with _MCPSession() as session:
            tools = session.tools_list()
            result = session.tools_call("generate_k8s_config", {"app_name": "demo"})
    """

    MCP_PROTOCOL_VERSION = "2024-11-05"

    def __init__(self) -> None:
        env = {**os.environ, "PYTHONPATH": _REPO_ROOT}
        self._proc = subprocess.Popen(
            [sys.executable, "-m", "mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=_REPO_ROOT,
        )
        self._next_id = 1

    # ------------------------------------------------------------------
    # Low-level transport helpers
    # ------------------------------------------------------------------

    def _send_request(self, method: str, params: Any = None) -> Dict:
        """Send a JSON-RPC request and return the parsed response line."""
        req_id = self._next_id
        self._next_id += 1
        msg: Dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            msg["params"] = params
        self._proc.stdin.write(json.dumps(msg) + "\n")
        self._proc.stdin.flush()
        raw = self._proc.stdout.readline()
        if not raw:
            stderr_out = self._proc.stderr.read()
            raise RuntimeError(
                f"MCP server produced no response for method '{method}'. "
                f"Server stderr: {stderr_out!r}"
            )
        return json.loads(raw)

    def _send_notification(self, method: str, params: Any = None) -> None:
        """Send a JSON-RPC notification (no id, no response expected)."""
        msg: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._proc.stdin.write(json.dumps(msg) + "\n")
        self._proc.stdin.flush()

    # ------------------------------------------------------------------
    # MCP handshake
    # ------------------------------------------------------------------

    def initialize(self) -> Dict:
        """Perform the MCP initialize / notifications/initialized handshake."""
        resp = self._send_request(
            "initialize",
            params={
                "protocolVersion": self.MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "pytest-mcp-test", "version": "1.0.0"},
            },
        )
        # Must send notifications/initialized before any tool calls
        self._send_notification("notifications/initialized")
        self._handshake_done = True
        return resp

    # ------------------------------------------------------------------
    # High-level MCP methods
    # ------------------------------------------------------------------

    def tools_list(self) -> Dict:
        """Call tools/list and return the full response."""
        return self._send_request("tools/list", params={})

    def tools_call(self, tool_name: str, arguments: Optional[Dict] = None) -> Dict:
        """Call tools/call for a given tool and return the full response."""
        return self._send_request(
            "tools/call",
            params={"name": tool_name, "arguments": arguments or {}},
        )

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "_MCPSession":
        self.initialize()
        return self

    def __exit__(self, *_) -> None:
        try:
            self._proc.stdin.close()
        except Exception:
            pass
        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMCPProtocolHandshake:
    """Prove the MCP initialize / notifications/initialized exchange works correctly."""

    def test_initialize_returns_protocol_version(self):
        """
        Proves: the server completes the MCP handshake and echoes the agreed
        protocol version (2024-11-05), which is the version Claude Code sends.
        A client that sees a mismatched version refuses to connect.
        """
        with _MCPSession() as session:
            # initialize() was already called by __enter__; re-verify via a new session
            pass  # session just completing without error is the proof

        # Verify directly without context manager
        s = _MCPSession()
        resp = s.initialize()
        try:
            assert "result" in resp, f"Expected 'result' in initialize response, got: {resp}"
            result = resp["result"]
            assert result["protocolVersion"] == _MCPSession.MCP_PROTOCOL_VERSION, (
                f"Protocol version mismatch: {result.get('protocolVersion')}"
            )
            assert "serverInfo" in result, "serverInfo missing from initialize response"
            assert result["serverInfo"]["name"] == "devops-os", (
                f"Unexpected server name: {result['serverInfo'].get('name')}"
            )
        finally:
            s._proc.terminate()
            s._proc.wait(timeout=5)

    def test_initialize_response_has_capabilities(self):
        """
        Proves: the server advertises its capabilities block so MCP clients
        know which features (tools, prompts, resources) are supported.
        """
        s = _MCPSession()
        resp = s.initialize()
        try:
            assert "result" in resp
            assert "capabilities" in resp["result"], (
                "capabilities block missing from initialize response"
            )
            caps = resp["result"]["capabilities"]
            assert "tools" in caps, "tools capability not advertised"
        finally:
            s._proc.terminate()
            s._proc.wait(timeout=5)


class TestMCPProtocolToolDiscovery:
    """Prove tools/list returns the correct set of DevOps-OS tools."""

    def test_tools_list_returns_all_expected_tools(self):
        """
        Proves: every DevOps-OS scaffold tool is registered and visible via
        the MCP tools/list call.  A missing entry here means a Claude user
        would not see (and could not invoke) that tool at all.
        """
        with _MCPSession() as session:
            resp = session.tools_list()

        assert "result" in resp, f"tools/list error: {resp}"
        tools = resp["result"]["tools"]
        names = {t["name"] for t in tools}
        missing = EXPECTED_TOOLS - names
        assert not missing, (
            f"These tools are missing from tools/list: {missing}\n"
            f"Registered tools: {names}"
        )

    def test_every_tool_has_description(self):
        """
        Proves: every tool carries a non-empty description string, which
        Claude uses to decide when to invoke each tool.  An empty description
        would cause Claude to ignore or misuse the tool.
        """
        with _MCPSession() as session:
            resp = session.tools_list()

        tools = resp["result"]["tools"]
        for tool in tools:
            assert tool.get("description"), (
                f"Tool '{tool['name']}' has no description — Claude won't know when to use it"
            )

    def test_every_tool_has_input_schema(self):
        """
        Proves: every tool exposes an inputSchema so MCP clients can validate
        arguments before sending them and display parameter hints to users.
        """
        with _MCPSession() as session:
            resp = session.tools_list()

        tools = resp["result"]["tools"]
        for tool in tools:
            assert "inputSchema" in tool, (
                f"Tool '{tool['name']}' is missing inputSchema"
            )


class TestMCPProtocolToolInvocation:
    """
    Prove that each tool can be invoked over the wire and returns valid artifact content.

    Each test sends a real tools/call JSON-RPC request and asserts that:
      - The response has a ``result`` (not an ``error``)
      - The result content contains expected artifact keywords
    """

    def _call_tool(self, tool_name: str, arguments: Optional[Dict] = None) -> str:
        """Invoke a tool and return the text content of the first content item."""
        with _MCPSession() as session:
            resp = session.tools_call(tool_name, arguments or {})
        assert "result" in resp, (
            f"tools/call '{tool_name}' returned error: {resp.get('error')}"
        )
        content = resp["result"].get("content", [])
        assert content, f"tools/call '{tool_name}' returned empty content"
        text = content[0].get("text", "")
        assert text, f"tools/call '{tool_name}' returned empty text"
        return text

    # ---- GitHub Actions ------------------------------------------------

    def test_call_generate_github_actions_workflow(self):
        """
        Proves: the GHA tool generates a YAML workflow file over the MCP
        wire protocol with the requested app name and language embedded.
        """
        text = self._call_tool(
            "generate_github_actions_workflow",
            {"name": "mcp-test-app", "workflow_type": "build", "languages": "python"},
        )
        assert "mcp-test-app" in text, "app name not in GHA workflow output"
        assert "runs-on:" in text, "not a valid GitHub Actions YAML (missing runs-on)"

    # ---- Jenkins -------------------------------------------------------

    def test_call_generate_jenkins_pipeline(self):
        """
        Proves: the Jenkins tool returns a valid Declarative Pipeline (Jenkinsfile)
        with the pipeline { ... } block required by Jenkins.
        """
        text = self._call_tool(
            "generate_jenkins_pipeline",
            {"name": "java-service", "pipeline_type": "build", "languages": "java"},
        )
        assert "pipeline" in text.lower(), "Jenkinsfile 'pipeline' block missing"
        assert "agent" in text.lower(), "Jenkinsfile 'agent' directive missing"

    # ---- Kubernetes ----------------------------------------------------

    def test_call_generate_k8s_config(self):
        """
        Proves: the Kubernetes tool returns a Deployment manifest with the
        requested app name and container image, confirming round-trip parameter
        passing through the MCP wire protocol.
        """
        text = self._call_tool(
            "generate_k8s_config",
            {
                "app_name": "api-service",
                "image": "ghcr.io/myorg/api-service:v1.0.0",
                "replicas": 2,
                "port": 8080,
            },
        )
        assert "api-service" in text, "app name not in K8s manifest"
        assert "Deployment" in text, "Deployment kind missing from K8s manifest"
        assert "ghcr.io/myorg/api-service:v1.0.0" in text, "image not in K8s manifest"

    # ---- GitLab CI -----------------------------------------------------

    def test_call_generate_gitlab_ci_pipeline(self):
        """
        Proves: the GitLab CI tool returns a .gitlab-ci.yml with stage definitions.
        """
        text = self._call_tool(
            "generate_gitlab_ci_pipeline",
            {"name": "py-service", "pipeline_type": "test", "languages": "python"},
        )
        assert "stages:" in text, ".gitlab-ci.yml stages block missing"

    # ---- ArgoCD --------------------------------------------------------

    def test_call_generate_argocd_config(self):
        """
        Proves: the ArgoCD tool returns a JSON bundle containing both an
        Application and an AppProject manifest, proving JSON envelope wrapping
        through the MCP protocol is intact.
        """
        text = self._call_tool(
            "generate_argocd_config",
            {"app_name": "my-app", "repo_url": "https://github.com/org/repo"},
        )
        data = json.loads(text)
        assert "argocd/application.yaml" in data, "application.yaml missing from ArgoCD bundle"
        assert "argocd/appproject.yaml" in data, "appproject.yaml missing from ArgoCD bundle"
        assert "Application" in data["argocd/application.yaml"]

    # ---- SRE configs ---------------------------------------------------

    def test_call_generate_sre_configs(self):
        """
        Proves: the SRE tool returns a JSON bundle with Prometheus alert rules,
        a Grafana dashboard JSON, and an SLO manifest — three separate artifact
        types in one call.
        """
        text = self._call_tool(
            "generate_sre_configs",
            {"name": "payment-service", "slo_type": "availability", "slo_target": 99.9},
        )
        data = json.loads(text)
        assert "alert_rules_yaml" in data, "Prometheus alert rules missing from SRE bundle"
        assert "grafana_dashboard_json" in data, "Grafana dashboard missing from SRE bundle"
        assert "slo_yaml" in data, "SLO manifest missing from SRE bundle"
        assert "PrometheusRule" in data["alert_rules_yaml"]

    # ---- Dev container -------------------------------------------------

    def test_call_scaffold_devcontainer(self):
        """
        Proves: the devcontainer tool returns a valid JSON bundle with both
        devcontainer.json and devcontainer.env.json files, confirming the
        JSON-in-JSON envelope survives the MCP wire protocol.
        """
        text = self._call_tool(
            "scaffold_devcontainer",
            {"languages": "python,go", "cicd_tools": "docker,github_actions"},
        )
        data = json.loads(text)
        assert "devcontainer_json" in data, "devcontainer.json missing from bundle"
        assert "devcontainer_env_json" in data, "devcontainer.env.json missing from bundle"

    # ---- Unit test config ----------------------------------------------

    def test_call_generate_unittest_config(self):
        """
        Proves: the unittest scaffold tool returns pytest configuration for
        a Python project over the MCP wire protocol.
        """
        text = self._call_tool(
            "generate_unittest_config",
            {"name": "data-pipeline", "languages": "python"},
        )
        data = json.loads(text)
        assert any("pytest" in k or "conftest" in k or "pyproject" in k for k in data), (
            f"No pytest config file found in unittest output keys: {list(data.keys())}"
        )


class TestMCPProtocolErrorHandling:
    """Prove the server handles invalid requests gracefully without crashing."""

    def test_call_unknown_tool_returns_error(self):
        """
        Proves: calling a tool that does not exist returns a proper JSON-RPC
        error response rather than crashing the server or hanging.  After the
        error, the server must still be alive for subsequent calls.
        """
        with _MCPSession() as session:
            resp = session.tools_call("this_tool_does_not_exist", {})
            # Should be an error response
            assert "error" in resp or (
                "result" in resp and resp["result"].get("isError")
            ), (
                f"Expected error for unknown tool, got: {resp}"
            )
            # Server must still respond to subsequent requests
            list_resp = session.tools_list()
            assert "result" in list_resp, (
                "Server became unresponsive after an error response"
            )


class TestMCPProtocolSequentialCalls:
    """Prove the server handles multiple back-to-back calls in one session."""

    def test_multiple_sequential_tool_calls(self):
        """
        Proves: a single MCP session can handle multiple back-to-back
        ``tools/call`` requests without restarting.  This mirrors real usage
        where a user asks Claude several follow-up questions that each trigger
        a DevOps-OS tool invocation.
        """
        calls = [
            ("generate_github_actions_workflow", {"name": "seq-app", "languages": "python"}),
            ("generate_jenkins_pipeline", {"name": "seq-svc", "languages": "java"}),
            ("generate_k8s_config", {"app_name": "seq-k8s", "image": "nginx:latest"}),
        ]
        with _MCPSession() as session:
            for tool_name, args in calls:
                resp = session.tools_call(tool_name, args)
                assert "result" in resp, (
                    f"Sequential call to '{tool_name}' returned error: {resp.get('error')}"
                )
                content = resp["result"].get("content", [])
                assert content and content[0].get("text"), (
                    f"Sequential call to '{tool_name}' returned empty content"
                )
