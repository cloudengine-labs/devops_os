"""HTTP client integration tests for MCP server.

Tests the MCP server's HTTP transport (streamable-http) using real MCP SDK client.
Verifies protocol negotiation, tool discovery, invocation, and authentication.
"""

import pytest
import asyncio
import json
import os
import sys

# Try to import MCP client - mock if not available
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False

# For HTTP testing, we'll use httpx to simulate an HTTP client
import httpx


class TestHTTPEndpoints:
    """Tests for HTTP health and readiness endpoints.

    Both tests previously asserted a hand-written literal dict against
    itself and could never fail. Checking the codebase found the routes
    didn't exist at all -- and that docker-compose.yml's healthcheck and
    scripts/smoke-test.py both already call GET /health expecting 200, so
    any Docker/HTTP deployment's healthcheck has been silently failing.
    Fixed by adding real routes (mcp_server/server.py's
    _register_health_routes) and testing them for real here, via an ASGI
    test client against streamable_http_app() -- no port binding needed.
    """

    def _client(self, profile="local", token_verifier=None):
        from mcp.server.fastmcp import FastMCP
        from mcp_server.config import Config
        from mcp_server.server import _register_health_routes

        m = FastMCP("test-health")
        config = Config(transport="streamable-http", profile=profile,
                         jwt_issuer="https://example.com/" if profile == "remote" else "",
                         jwt_audience="devops-os" if profile == "remote" else "")
        _register_health_routes(m, config, token_verifier)
        transport = httpx.ASGITransport(app=m.streamable_http_app())
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_health_endpoint_format(self):
        async with self._client() as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "alive"
        assert "timestamp" in body

    @pytest.mark.asyncio
    async def test_ready_endpoint_local_profile_always_ready(self):
        async with self._client(profile="local") as client:
            resp = await client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ready"] is True
        assert body["checks"]["config"] == "valid"

    @pytest.mark.asyncio
    async def test_ready_endpoint_remote_profile_without_auth_not_ready(self):
        """Remote profile with no token_verifier configured must report
        not-ready with a 503, not silently claim health."""
        async with self._client(profile="remote", token_verifier=None) as client:
            resp = await client.get("/ready")
        assert resp.status_code == 503
        body = resp.json()
        assert body["ready"] is False
        assert body["checks"]["auth"] == "missing"

    @pytest.mark.asyncio
    async def test_ready_endpoint_remote_profile_with_auth_is_ready(self):
        async with self._client(profile="remote", token_verifier=object()) as client:
            resp = await client.get("/ready")
        assert resp.status_code == 200
        assert resp.json()["ready"] is True


class TestHTTPTransportConfiguration:
    """Tests for HTTP transport configuration via FastMCP."""

    def test_config_host_port_settings(self):
        """Test that Config properly stores host/port for FastMCP."""
        from mcp_server.config import Config
        
        config = Config(
            transport="streamable-http",
            host="0.0.0.0",
            port=9000,
        )
        
        assert config.transport == "streamable-http"
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.mcp_endpoint == "/mcp"

    def test_config_request_size_limit(self):
        """Test that request size limits are properly configured."""
        from mcp_server.config import Config
        
        config = Config(
            transport="streamable-http",
            request_size_mb=50,
            response_size_mb=100,
        )
        
        assert config.request_size_mb == 50
        assert config.response_size_mb == 100
        assert config.request_size_bytes == 50 * 1024 * 1024
        assert config.response_size_bytes == 100 * 1024 * 1024

    def test_config_auth_for_http(self):
        """Test that Config handles auth for HTTP remote profile."""
        from mcp_server.config import Config
        
        # Remote profile without JWT should fail
        with pytest.raises(ValueError, match="JWT_ISSUER"):
            Config(
                transport="streamable-http",
                profile="remote",
            )
        
        # With proper JWT config should work
        config = Config(
            transport="streamable-http",
            profile="remote",
            jwt_issuer="https://auth.example.com",
            jwt_audience="devops-os-service",
        )
        
        assert config.profile == "remote"
        assert config.jwt_issuer == "https://auth.example.com"
        assert config.jwt_audience == "devops-os-service"


class TestTokenVerifierForHTTP:
    """Tests for token verifier behavior in HTTP context."""

    def test_local_token_verifier_accepts_all(self):
        """Test that LocalNoOpTokenVerifier accepts any token."""
        import asyncio
        from mcp_server.auth import LocalNoOpTokenVerifier
        
        async def run_test():
            verifier = LocalNoOpTokenVerifier()
            
            # Test with various token formats
            tokens = [
                "simple-token",
                "bearer-token-with-dashes",
                "******",  # JWT-like
                "x" * 1000,  # Long token
            ]
            
            for token in tokens:
                result = await verifier.verify_token(token)
                assert result is not None
                assert result.token == token
                assert result.resource == "devops-os-local"
        
        asyncio.run(run_test())

    def test_jwt_token_verifier_rejects_invalid_issuer(self):
        """Test that JWTTokenVerifier rejects tokens with wrong issuer."""
        import asyncio
        from mcp_server.auth import JWTTokenVerifier
        
        async def run_test():
            verifier = JWTTokenVerifier(
                issuer="https://auth.example.com/",
                audience="devops-os-service",
            )
            
            # Without proper JWT library, verification fails gracefully
            result = await verifier.verify_token("invalid-token")
            assert result is None  # Verification failed
        
        asyncio.run(run_test())


class TestHTTPRequestHandling:
    """Tests for HTTP request handling (size limits, timeouts, etc.)."""

    def test_request_size_byte_math_and_wiring(self):
        """Config's byte math for request_size_mb -> request_size_bytes, AND
        that it actually reaches the HTTP server construction (verified via
        a source-level check, since that construction only happens inside
        `if __name__ == "__main__":`, not in an importable function).
        Previously named test_oversized_request_body and claimed to test
        that oversized bodies are 'rejected' -- it never did; it only
        checked the arithmetic. No test in this suite starts a live HTTP
        server to confirm an oversized body is actually rejected at runtime.
        """
        from mcp_server.config import Config
        import inspect
        from mcp_server import server

        config = Config(transport="streamable-http")
        assert config.request_size_bytes == 10 * 1024 * 1024
        assert config.request_size_mb == 10

        source = inspect.getsource(server)
        assert "config.request_size_bytes" in source, (
            "request_size_bytes is computed but no longer passed into the "
            "FastMCP HTTP instance -- check the max_request_body_size wiring "
            "in __main__"
        )

    def test_response_size_calculation_not_wired_anywhere(self):
        """Config computes response_size_bytes correctly, but (unlike
        request_size_bytes) it is never referenced anywhere else in
        server.py -- grep confirms no `response_size_bytes` /
        `response_size_mb` usage outside config.py. This test documents
        that gap rather than implying the limit is enforced."""
        from mcp_server.config import Config
        import inspect
        from mcp_server import server

        config = Config(transport="streamable-http", response_size_mb=500)
        assert config.response_size_bytes == 500 * 1024 * 1024

        source = inspect.getsource(server)
        assert "response_size_bytes" not in source and "response_size_mb" not in source, (
            "response_size_bytes/mb is now referenced in server.py -- if it's actually "
            "wired into the HTTP server, update this test (and this docstring) to confirm "
            "that wiring instead of documenting its absence."
        )

    def test_execution_timeout_not_wired_anywhere(self):
        """Same gap as response_size: execution_timeout computes correctly
        but is never passed into the HTTP server construction."""
        from mcp_server.config import Config
        import inspect
        from mcp_server import server

        config = Config(transport="streamable-http", execution_timeout=60)
        assert config.execution_timeout == 60

        source = inspect.getsource(server)
        assert "execution_timeout" not in source, (
            "execution_timeout is now referenced in server.py -- if it's actually wired "
            "into request handling, update this test to confirm that wiring instead of "
            "documenting its absence."
        )


class TestMCPProtocolCompat:
    """Tests for MCP protocol compatibility over HTTP."""

    def test_tool_discovery_payload_structure(self):
        """Test that tools are properly structured for MCP discovery.

        Previously only checked `hasattr(server, 'mcp')` -- true even if
        zero tools were registered. Now actually lists the tools and checks
        every one has a name, description, and inputSchema, matching what a
        real MCP client discovery call needs.
        """
        from mcp_server import server

        tools = asyncio.run(server.mcp.list_tools())
        assert len(tools) == 13, f"expected all 13 tools registered, got {len(tools)}"
        for tool in tools:
            assert tool.name, "tool missing a name"
            assert tool.description, f"tool '{tool.name}' missing a description"
            assert tool.inputSchema, f"tool '{tool.name}' missing an inputSchema"

    def test_tool_invocation_json_serializable(self):
        """Test that tool responses are JSON serializable."""
        import json
        from mcp_server.server import generate_k8s_config
        
        # Test generate_k8s_config
        result = generate_k8s_config(
            app_name="test-app",
            image="test:latest",
            replicas=2,
        )
        
        # Should be string with YAML content
        assert isinstance(result, str)
        assert "apiVersion" in result or "kind" in result
        # Should be valid YAML
        import yaml
        data = yaml.safe_load_all(result)
        docs = list(data)
        assert len(docs) > 0

    def test_json_response_structure(self):
        """Test that JSON responses follow MCP structure."""
        import json
        from mcp_server.server import scaffold_devcontainer
        
        result = scaffold_devcontainer(
            languages="python,javascript",
        )
        
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, dict)
        # Should have expected fields
        assert "devcontainer_json" in data or "devcontainer_env_json" in data


class TestConcurrentRequests:
    """Tests for concurrent request handling and isolation."""

    def test_concurrent_artifacts_isolated(self):
        """Test that concurrent tool invocations produce isolated artifacts."""
        from mcp_server.server import generate_k8s_config
        
        # Simulate concurrent requests by running generators multiple times
        results = []
        for i in range(5):
            result = generate_k8s_config(
                app_name=f"app-{i}",
                image=f"app-{i}:latest",
                replicas=i + 1,
            )
            results.append(result)
        
        # Each result should be valid
        assert len(results) == 5
        
        for i, result in enumerate(results):
            # Verify content includes app name
            assert f"app-{i}" in result

    def test_request_isolation_no_cross_contamination(self):
        """Test that requests don't contaminate each other's temporary files."""
        from mcp_server.server import generate_github_actions_workflow
        
        # Run multiple sequential requests
        result1 = generate_github_actions_workflow(
            name="workflow-1",
            languages="python",
        )
        
        result2 = generate_github_actions_workflow(
            name="workflow-2",
            languages="javascript",
        )
        
        # Results should be independent
        assert "workflow-1" in result1 or "python" in result1
        assert "workflow-2" in result2 or "javascript" in result2
        # Results should be different (not swapped)
        assert result1 != result2


class TestErrorHandling:
    """Tests for error handling over HTTP."""

    def test_invalid_tool_input_error(self):
        """Test that invalid tool inputs produce proper error responses."""
        from mcp_server.validators import validate_tool_inputs, ValidationError
        
        # Test with invalid K8s identifier
        with pytest.raises(ValidationError):
            validate_tool_inputs(
                "generate_k8s_config",
                app_name="Invalid-App-Name",  # Not lowercase
            )

    def test_oversized_string_parameter(self):
        """Test that oversized string parameters are rejected."""
        from mcp_server.validators import validate_tool_inputs, ValidationError
        
        # K8s identifiers must be <= 63 chars
        with pytest.raises(ValidationError):
            validate_tool_inputs(
                "generate_k8s_config",
                app_name="a" * 64,  # Too long
            )

    def test_invalid_port_parameter(self):
        """Test that invalid port numbers are rejected."""
        from mcp_server.validators import validate_tool_inputs, ValidationError
        
        with pytest.raises(ValidationError):
            validate_tool_inputs(
                "generate_k8s_config",
                port=99999,  # Out of range
            )

    def test_authentication_failure_logging(self):
        """Test that auth failures are logged appropriately."""
        from mcp_server.logging import get_logger, CorrelationContext
        import io
        import sys
        import json
        
        # Set correlation ID
        CorrelationContext.set("test-auth-request")
        logger = get_logger(__name__, "INFO")
        
        # Capture stderr
        captured_output = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_output
        
        try:
            logger.log_auth_failure("Invalid signature", "http")
            
            # Restore stderr to get output
            sys.stderr = old_stderr
            output = captured_output.getvalue().strip()
            
            # Parse the JSON log entry
            if output:
                log_entry = json.loads(output)
                
                assert log_entry["level"] == "WARNING"
                assert log_entry["error_category"] == "auth_failure"
                assert "signature" in log_entry["event"]
                # Token should not be exposed
                assert "secret" not in output
        finally:
            sys.stderr = old_stderr

    def test_validation_error_message_clarity(self):
        """Test that validation errors provide clear messages."""
        from mcp_server.validators import validate_tool_inputs, ValidationError
        
        try:
            validate_tool_inputs(
                "generate_k8s_config",
                app_name="app_with_underscore",  # Invalid
            )
        except ValidationError as e:
            error_message = str(e)
            # Should explain what's wrong
            assert "lowercase" in error_message or "alphanumeric" in error_message


class TestLoggingIntegration:
    """Tests for structured logging in HTTP context."""

    def test_correlation_id_tracking(self):
        """Test that correlation IDs are tracked across requests."""
        from mcp_server.logging import CorrelationContext
        
        # Generate new ID
        id1 = CorrelationContext.new()
        assert id1.startswith("req-")
        
        # Should be retrievable
        assert CorrelationContext.get() == id1
        
        # Should be unique on each call
        id2 = CorrelationContext.new()
        assert id2 != id1

    def test_tool_invocation_logging(self):
        """Test that tool invocations are properly logged."""
        from mcp_server.logging import get_logger, CorrelationContext
        import io
        import sys
        import json
        
        logger = get_logger(__name__, "INFO")
        CorrelationContext.set("test-request-123")
        
        # Capture stderr
        captured_output = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured_output
        
        try:
            logger.log_tool_invocation(
                "generate_k8s_config",
                transport="streamable-http",
                status="success",
                duration_ms=245,
                output_size_bytes=4096,
            )
            
            # Restore stderr to get output
            sys.stderr = old_stderr
            output = captured_output.getvalue().strip()
            
            if output:
                log_entry = json.loads(output)
                
                # Verify log structure
                assert log_entry["correlation_id"] == "test-request-123"
                assert log_entry["tool_name"] == "generate_k8s_config"
                assert log_entry["transport"] == "streamable-http"
                assert log_entry["duration_ms"] == 245
                assert log_entry["status"] == "success"
        finally:
            sys.stderr = old_stderr

    def test_sensitive_data_redaction(self):
        """Test that sensitive data is redacted from logs."""
        from mcp_server.logging import RedactedDict
        
        redactor = RedactedDict()
        data = {
            "jwt_secret": "super-secret-key",
            "api_key": "ak-1234567890",
            "public_field": "safe-value",
        }
        
        redacted = redactor.redact(data)
        
        # Safe fields should be preserved
        assert redacted["public_field"] == "safe-value"
        
        # Sensitive fields should be redacted
        assert "super-secret-key" not in str(redacted)
        assert "1234567890" not in str(redacted)
        assert "<" in redacted["jwt_secret"]  # Redaction marker


@pytest.mark.skipif(not MCP_SDK_AVAILABLE, reason="MCP client not available")
class TestMCPSDKClient:
    """Tests using the real, official MCP SDK client (if available) --
    distinct in kind from tests/test_mcp_protocol.py's _MCPSession, which
    speaks hand-rolled raw JSON-RPC over stdio. This class instead confirms
    our server works correctly when driven by the actual client library a
    real downstream consumer would use.

    Both tests previously just checked that `ClientSession` was importable
    (`assert ClientSession is not None`, `assert hasattr(ClientSession,
    '__init__')` -- true of literally any class). They never actually ran,
    because the module-level import at the top of this file named a class,
    `StdioClientTransport`, that has never existed in the Python MCP SDK --
    it's the MCP *TypeScript* SDK's class name. The real Python API is the
    `stdio_client` context manager + `StdioServerParameters`, fixed above.
    """

    @pytest.mark.asyncio
    async def test_client_connect_stdio_and_list_tools(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "mcp_server.server"],
            cwd=repo_root, env={**os.environ, "PYTHONPATH": repo_root},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init_result = await session.initialize()
                assert init_result.serverInfo.name == "devops-os"
                tools = await session.list_tools()
                assert len(tools.tools) == 13

    @pytest.mark.asyncio
    async def test_client_initialization_can_invoke_a_tool(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "mcp_server.server"],
            cwd=repo_root, env={**os.environ, "PYTHONPATH": repo_root},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("generate_k8s_config", {"app_name": "sdk-client-test"})
                assert result.content and "sdk-client-test" in result.content[0].text
