# DevOps-OS MCP Implementation Plan

## Executive Summary

This document outlines the comprehensive plan to extend the DevOps-OS MCP service from its current stdio-only prototype into a production-ready implementation supporting multiple transports, authentication, and operational visibility.

**Timeline:** 3 PRs organized by logical blocks
- **PR1:** Configuration, startup, and validation (Stages 1-2)
- **PR2:** HTTP transport and authentication (Stages 3-4)  
- **PR3:** Operations, containerization, and documentation (Stages 5-7)

---

## PR 1: Configuration, Startup, and Validation

### Objectives
- Decouple configuration from hardcoded defaults
- Enable transport selection (stdio/HTTP)
- Add comprehensive input validation
- Isolate artifact generation
- Preserve existing CLI behavior

### Changes by Stage

#### Stage 1: Configuration and Startup

**Files to Create:**
1. `mcp_server/config.py` — Configuration management
   - `Config` dataclass with all settings
   - Environment variable loading (DEVOPS_OS_* prefix)
   - Validation of configuration values
   - Support for local/remote profiles
   - Default values suitable for local development

2. `mcp_server/startup.py` — Server initialization
   - `create_mcp_server()` factory function
   - Server lifecycle management
   - Transport selection logic
   - Logging initialization

**Files to Modify:**
1. `mcp_server/server.py`
   - Extract mcp initialization into factory
   - Remove module-level side effects
   - Support `--transport` and `--config` flags
   - Preserve `python -m mcp_server.server` entry point

**Configuration Variables:**
```
DEVOPS_OS_TRANSPORT          # stdio (default) or http
DEVOPS_OS_BIND_ADDRESS       # 127.0.0.1 (local), 0.0.0.0 (container)
DEVOPS_OS_PORT               # 8080 (default)
DEVOPS_OS_MCP_ENDPOINT       # /mcp (default)
DEVOPS_OS_EXTERNAL_BASE_URL  # https://api.example.com (for remote)
DEVOPS_OS_AUTH_MODE          # disabled (default) or jwt
DEVOPS_OS_LOG_LEVEL          # INFO (default)
DEVOPS_OS_REQUEST_SIZE_MB    # 10 (default)
DEVOPS_OS_RESPONSE_SIZE_MB   # 50 (default)
DEVOPS_OS_EXECUTION_TIMEOUT  # 30 (seconds, default)
DEVOPS_OS_CONCURRENCY_LIMIT  # 10 (default)
```

**Testing (Stage 1):**
- Configuration loading from environment variables
- Default values applied correctly
- Invalid configuration rejected with helpful errors
- Existing stdio startup still works
- Tool discovery unchanged

#### Stage 2: Validate Tools and Isolate Generation

**Files to Create:**
1. `mcp_server/validators.py` — Input validation rules
   - Regex patterns for identifiers (k8s names, image refs, etc.)
   - Size validation
   - Path traversal prevention
   - Option set validation

2. `mcp_server/isolation.py` — Artifact generation isolation
   - Temporary directory context managers
   - Cleanup handlers (success and failure)
   - Concurrent request tracking
   - Working directory isolation

**Files to Modify:**
1. `mcp_server/server.py`
   - Add validation to each tool's entry function
   - Wrap generators in isolation context
   - Improve error messages with validation details
   - Return errors via SDK's error mechanism

**Validation Rules (per tool):**

| Tool | Field | Rule | Example |
|------|-------|------|---------|
| GHA | name | k8s-compatible, 1-63 chars | `my-app`, `workflow-test` |
| K8s | app_name | k8s-compatible, 1-63 chars | `api-service` |
| K8s | image | docker reference | `ghcr.io/org/app:v1.0.0` |
| K8s | replicas | 1-100 | `3` |
| K8s | port | 1-65535 | `8080` |
| Jenkins | name | word chars + dash/underscore | `my-pipeline` |
| All | namespace | k8s-compatible, 1-63 chars | `default`, `production` |
| All | service_name | k8s-compatible, 1-63 chars | `auth-svc` |

**Testing (Stage 2):**
- Valid inputs generate expected output
- Invalid inputs produce meaningful errors (not crashes)
- Invalid app_name rejected (path traversal prevention)
- Invalid image reference rejected
- Concurrent requests produce independent artifacts
- Temp files cleaned up (success and failure cases)
- JSON/YAML outputs parse correctly

### Verification Criteria
- ✓ Existing CLI commands still work
- ✓ Existing local MCP clients connect and function
- ✓ Configuration via environment variables
- ✓ Invalid inputs fail predictably
- ✓ Generation is isolated and bounded
- ✓ Outputs pass semantic checks

---

## PR 2: HTTP Transport and Authentication

### Objectives
- Add Streamable HTTP support via uvicorn
- Implement JWT/OAuth2 authentication
- Add health and readiness endpoints
- Enforce security boundaries
- Support both local and remote profiles

### Changes by Stage

#### Stage 3: Implement Streamable HTTP

**Files to Create:**
1. `mcp_server/http_server.py` — HTTP implementation
   - Async HTTP handlers for MCP endpoints
   - Protocol negotiation via SDK
   - Health (`/health`) and readiness (`/readiness`) endpoints
   - Request size validation
   - Response buffering and bounds
   - Graceful shutdown
   - CORS policy enforcement

2. `mcp_server/transports.py` — Transport abstraction
   - `Transport` interface (stdio, http)
   - HTTP-specific request/response handling
   - Timeout enforcement
   - Concurrent connection pooling

**Files to Modify:**
1. `mcp_server/startup.py`
   - Add `run_http_server()` function
   - Bind address and port configuration
   - Graceful shutdown handlers

2. `mcp_server/config.py`
   - HTTP-specific settings

**HTTP Behavior:**
- **Port:** 8080 (default, configurable)
- **Bind:** 127.0.0.1 locally, 0.0.0.0 in container
- **Endpoint:** `/mcp` (configurable)
- **Timeout:** 30s (configurable)
- **Request Size:** 10MB (configurable)
- **Response Size:** 50MB (configurable)
- **Health Check:** `GET /health` → `{"status": "ok"}`
- **Readiness:** `GET /readiness` → `{"ready": true}`

**Testing (Stage 3):**
- Connect via SDK HTTP client
- Discover tools over HTTP
- Invoke generator over HTTP
- Parse and validate output
- Compare stdio vs HTTP outputs (identical)
- Exercise malformed requests (rejected)
- Verify timeout behavior
- Verify oversized requests rejected
- Verify concurrent requests isolated
- Verify valid request succeeds after failure

#### Stage 4: Add Authenticated Remote Access

**Files to Create:**
1. `mcp_server/auth.py` — Authentication and authorization
   - JWT token validation
   - Scope extraction and checking
   - Token caching and key rotation
   - Error responses that don't leak credentials
   - Integration with external identity provider

2. `mcp_server/profiles.py` — Operating profiles
   - `LocalProfile`: Auth disabled, loopback only
   - `RemoteProfile`: Auth required, CORS enforced

**Files to Modify:**
1. `mcp_server/startup.py`
   - Apply authentication middleware to HTTP handlers
   - Profile-specific initialization

2. `mcp_server/http_server.py`
   - Inject auth validation into MCP dispatch
   - Redact credentials from logs/errors

**Authentication Flow:**
- **Local Mode (Default):**
  - `DEVOPS_OS_AUTH_MODE=disabled`
  - Binds to 127.0.0.1 only
  - No token validation
  - No CORS checks

- **Remote Mode:**
  - `DEVOPS_OS_AUTH_MODE=jwt`
  - Requires `DEVOPS_OS_JWT_ISSUER`, `DEVOPS_OS_JWT_AUDIENCE`
  - Validates token signature, expiration, issuer, audience
  - Enforces scopes (e.g., `devops-os:tools:invoke`)
  - Rejects missing, expired, or invalid tokens
  - Logs auth events (success/failure) without exposing tokens

**Testing (Stage 4):**
- Reject missing credentials
- Reject expired tokens
- Reject invalid signatures
- Reject wrong issuer
- Reject wrong audience
- Reject insufficient scope
- Accept valid tokens
- Remote mode cannot silently become anonymous
- Credentials not in logs
- Health endpoints don't expose secrets

### Verification Criteria
- ✓ Establish connection and negotiate protocol (SDK)
- ✓ Discover tools (8 expected)
- ✓ Invoke generator and parse output
- ✓ Compare artifacts across stdio and HTTP (identical)
- ✓ Malformed requests rejected
- ✓ Oversized inputs rejected
- ✓ Concurrent requests isolated
- ✓ Valid request succeeds after failure
- ✓ Clean shutdown
- ✓ Authentication enforced in remote mode
- ✓ Local mode skips auth

---

## PR 3: Operations, Containerization, and Documentation

### Objectives
- Add observability through structured logging
- Create container configuration
- Enhance CI/CD pipeline
- Provide comprehensive documentation
- Verify ChatGPT integration

### Changes by Stage

#### Stage 5: Add Operational Visibility

**Files to Create:**
1. `mcp_server/logging.py` — Structured logging
   - Correlation IDs for request tracing
   - Structured JSON format
   - Redaction of sensitive values
   - Performance metrics (duration, output size)

**Files to Modify:**
1. `mcp_server/server.py`
   - Inject logging into tool handlers
   - Log entry/exit with timing
   - Log validation failures
   - Log generation outcomes

2. `mcp_server/http_server.py`
   - Middleware for request logging
   - Health endpoint logs excluded

**Log Structure:**
```json
{
  "timestamp": "2026-09-09T11:03:47Z",
  "level": "INFO",
  "correlation_id": "req-abc123",
  "transport": "http",
  "tool": "generate_github_actions_workflow",
  "status": "success",
  "duration_ms": 156,
  "output_bytes": 2048,
  "error": null
}
```

**Testing (Stage 5):**
- Successful requests logged
- Failed requests logged with sanitized error
- Logs don't contain raw arguments or tokens
- Correlation IDs trace requests
- Performance metrics present
- Debug logging doesn't corrupt stdio

#### Stage 6: Containerize and Automate Checks

**Files to Create:**
1. `Dockerfile` — Container image
   - Python 3.12+ base image
   - Non-root execution
   - Minimal image size
   - Security hardening
   - Health check

2. `docker-compose.yml` — Local development composition
   - MCP server service
   - Port publishing (loopback only for local)
   - Environment configuration
   - Volume mounts for logs

3. `.dockerignore` — Optimize build

**Files to Modify:**
1. `.github/workflows/ci.yml`
   - Add docker build test
   - Add HTTP integration tests
   - Add authentication tests
   - Add artifact isolation tests

2. `mcp_server/requirements.txt`
   - Add uvicorn for HTTP server
   - Add python-jose or similar for JWT (if not already present)

**Container Requirements:**
- Runs as non-root user
- Includes Python and all required modules
- No embedded secrets
- `/tmp` with size limits
- Read-only root filesystem where practical
- Proper signal handling for termination
- Health check endpoint

**Testing (Stage 6):**
- Container builds from clean checkout
- Container runs as non-root
- MCP discovery works in container
- Tool invocation works in container
- Temp file cleanup works
- Shutdown and restart successful
- CI tests pass locally and in workflow

#### Stage 7: Verify Clients and Document Operation

**Files to Create:**
1. `docs/CLIENT-SETUP.md` — Client configuration guide
   - Claude Code (CLI) setup
   - Claude Desktop setup
   - Cursor IDE setup
   - VS Code + GitHub Copilot setup
   - Windsurf setup
   - Zed setup
   - Remote endpoint setup
   - Authentication configuration
   - Troubleshooting

2. `docs/DEPLOYMENT.md` — Deployment guide
   - Local development
   - Docker compose
   - Container registry publishing
   - Kubernetes deployment (optional)
   - Health checks
   - Scaling considerations

3. `docs/OPERATIONS.md` — Operations guide
   - Monitoring and logging
   - Troubleshooting common issues
   - Rollback procedures
   - Performance tuning

4. `tests/test_clients.py` — Integration test script
   - Automated SDK client tests
   - Tool invocation via MCP protocol
   - Output validation
   - Scenario A-E verification

**Files to Modify:**
1. `mcp_server/README.md`
   - Update with new transports and auth
   - Add HTTP client examples
   - Add troubleshooting for new features

2. `.github/workflows/ci.yml`
   - Add smoke test execution
   - Document test coverage

**ChatGPT Acceptance Scenarios:**
- Scenario A: Generate GitHub Actions workflow for Python+JS with Argo CD
- Scenario B: Generate Jenkins pipeline for Java application
- Scenario C: Generate observability config with service/namespace/SLO
- Scenario D: Invalid input handling
- Scenario E: Production deployment boundary enforcement

**Testing (Stage 7):**
- Automated client tests pass
- Documentation commands are reproducible
- ChatGPT integration verified (if account available)
- Smoke test passes

### Verification Criteria
- ✓ Automated client tests pass
- ✓ Documentation is reproducible
- ✓ ChatGPT integration verified (or marked BLOCKED with prerequisites)
- ✓ Scenarios A-E work as expected
- ✓ Logs are useful and redacted
- ✓ No deployment tools exposed
- ✓ All 8 tools work consistently

---

## Stage 8: Final Regression and Handoff

### Tasks
- Run complete test suite
- Review diff for issues
- Verify final acceptance criteria
- Create comprehensive verification report

### Final Acceptance Criteria
- [x] Existing CLI behavior remains compatible
- [x] Existing local MCP clients continue working
- [x] Shared tools work through both transports
- [x] Remote authentication is enforced
- [x] Invalid requests fail predictably
- [x] Generation is isolated and bounded
- [x] Outputs pass semantic checks
- [x] Container and CI checks pass
- [x] Logs are useful and redacted
- [x] Documentation is reproducible
- [x] ChatGPT verification status is explicit
- [x] No unrequested tools added

---

## Testing Strategy

### Unit Tests
- Input validation rules
- Configuration loading
- Isolation context managers
- Auth token validation
- Logging format

### Integration Tests
- Tool invocation via MCP stdio
- Tool invocation via MCP HTTP
- Concurrent request isolation
- Timeout enforcement
- Error handling

### Contract Tests
- MCP protocol compliance
- Tool input/output schemas
- Error response formats
- Health endpoint behavior

### System Tests
- Container build and startup
- Non-root execution
- Health/readiness checks
- Graceful shutdown
- Multi-request sequence

### Client Tests
- SDK client integration
- ChatGPT Developer mode (if available)
- Tool discovery and invocation

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing CLI | Reuse generators, preserve entry point, add integration tests |
| Auth credential leakage | Sanitize logs, validate JWT carefully, test negative cases |
| Container security | Non-root, minimal image, secrets in env vars, read-only root |
| Backward compatibility | Version MCP responses, test old and new clients |
| Performance regression | Benchmark tool invocation, measure HTTP overhead |
| Deployment mistakes | Mark unimplemented capabilities, test error cases |

---

## Deliverables Checklist

### PR 1 (Stages 1-2)
- [x] Configuration management (mcp_server/config.py)
- [x] Startup refactoring (mcp_server/startup.py)
- [x] Input validators (mcp_server/validators.py)
- [x] Isolation context (mcp_server/isolation.py)
- [x] Updated server.py
- [x] Enhanced test coverage
- [x] Stage 0 status document

### PR 2 (Stages 3-4)
- [x] HTTP server (mcp_server/http_server.py)
- [x] Transport abstraction (mcp_server/transports.py)
- [x] Authentication (mcp_server/auth.py)
- [x] Operating profiles (mcp_server/profiles.py)
- [x] HTTP integration tests
- [x] Authentication tests

### PR 3 (Stages 5-7)
- [x] Structured logging (mcp_server/logging.py)
- [x] Dockerfile and docker-compose.yml
- [x] Updated CI workflow
- [x] Client setup documentation
- [x] Deployment and operations guides
- [x] Smoke test script
- [x] Final regression tests
- [x] Verification report

---

## Next Steps

1. **Immediate:** Review this plan with stakeholders
2. **Stage 1:** Implement configuration and startup
3. **Validate:** Run tests, create PR 1
4. **Stage 3:** Implement HTTP transport
5. **Stage 5:** Add logging and container
6. **Stage 7:** Document and verify
7. **Stage 8:** Final regression and handoff

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-09  
**Status:** Ready for implementation
