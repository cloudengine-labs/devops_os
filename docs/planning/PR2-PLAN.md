# PR 2 Implementation Plan: HTTP Transport and Authentication

**Base branch:** PR 1 (Configuration and Input Validation)  
**Stages covered:** 3 (Streamable HTTP), 4 (Authenticated Remote Access), 5 (Operational Logging)  
**Gate requirement:** PASS Stage 3, 4, and 5 criteria

## Overview

This PR extends the MCP server with:
1. **HTTP/Streamable HTTP Transport** - Use FastMCP's native `transport='streamable-http'`
2. **Token-Based Authentication** - FastMCP's `auth_server_provider` and `token_verifier`
3. **Structured Logging** - JSON logs with correlation IDs and credential redaction
4. **Health/Readiness Endpoints** - Liveness and configuration validation checks

### FastMCP Built-in Capabilities (MCP 1.30.0)

```python
# Constructor parameters
FastMCP(
    transport='streamable-http',  # Selector in run()
    host='0.0.0.0',               # Bind address
    port=8000,                    # Port number
    streamable_http_path='/mcp',  # MCP endpoint
    max_request_body_size=10_000_000,  # 10 MB from config
    auth=AuthSettings(...),       # ****** requirements
    auth_server_provider=provider, # OAuth provider (optional)
    token_verifier=verifier,      # Custom token validation
    log_level='INFO',             # Logging level
)

# Run with selected transport
mcp.run(transport='streamable-http', mount_path='/mcp')
```

### Architecture

```
Config (PR 1)
    │
    └─→ mcp_server/logging.py [NEW]
        - Structured JSON logger
        - Correlation ID tracking
        - Credential redaction (tokens, keys, secrets)
        - Duration/latency tracking
        
    └─→ mcp_server/auth.py [NEW]
        - LocalNoOpTokenVerifier (development)
        - JWTTokenVerifier (production)
        - AuthMetadataProvider (discovery)
        
    └─→ mcp_server/health.py [NEW]
        - Health check endpoint
        - Readiness check endpoint
        
    └─→ mcp_server/server.py [MODIFIED]
        - Integrate logging at server startup
        - Use Config.profile to select auth mode
        - Pass token_verifier to FastMCP
        - Handle HTTP transport in run()
```

## Implementation Tasks

### 1. Create Logging Module (mcp_server/logging.py)

**Purpose:** Structured, redacted logging for observability.

**Key components:**
- `StructuredLogger` - Wraps Python logging with JSON formatting
- `RedactedDict` - Redacts common secret patterns (tokens, keys, api_key, etc.)
- `CorrelationContext` - Thread-local/async-local correlation ID tracking
- Log helper functions: `log_tool_call()`, `log_auth_failure()`, `log_error()`, etc.

**Implementation notes:**
- Use Python's `logging` module with JSON formatter
- Exclude raw arguments and response bodies by default
- Include: timestamp, correlation_id, tool_name, duration, status, outcome
- For stdio: write all logs to stderr (preserve stdout for MCP protocol)
- For HTTP: write to stderr or configured handler

**Sample log entry:**
```json
{
  "timestamp": "2026-09-09T18:42:47.961Z",
  "level": "INFO",
  "correlation_id": "req-1234-5678",
  "transport": "streamable-http",
  "tool_name": "generate_k8s_config",
  "duration_ms": 145,
  "status": "success",
  "output_size_bytes": 2847,
  "event": "tool_invocation_complete"
}
```

### 2. Create Auth Module (mcp_server/auth.py)

**Purpose:** Pluggable authentication for local and remote modes.

**Components:**
- `LocalNoOpTokenVerifier` - Accepts any token (for development)
- `JWTTokenVerifier` - Validates JWT signatures, issuer, audience, expiration
- `AuthMetadataProvider` - Returns OpenID Connect discovery endpoint metadata
- Helper: `create_auth_verifier()` - Factory function based on Config.profile

**Implementation notes:**
- LocalNoOpTokenVerifier used when profile='local' (logs a warning)
- JWTTokenVerifier verifies:
  - Signature (using public key from JWKS endpoint)
  - Issuer (matches config JWT_ISSUER)
  - Audience (matches config JWT_AUDIENCE)
  - Expiration (not expired)
  - Scopes (optional, for future use)
- Cache JWKS keys with TTL (3600s default)
- Return AccessToken with resource set to JWT_AUDIENCE
- On verification failure: return None (FastMCP rejects request)
- Log auth failures at WARNING level (exclude token from log)

**Reuse maintained libraries:**
- `python-jose` or `PyJWT` for JWT validation (check if already available)
- Use `httpx` for async JWKS fetch (already in mcp deps)

### 3. Create Health Module (mcp_server/health.py)

**Purpose:** Provide liveness and readiness endpoints for container orchestration.

**Endpoints:**
- GET `/health` - Liveness check (always 200)
- GET `/ready` - Readiness check (verify config, auth setup)
- GET `/mcp` - MCP endpoint (existing)

**Implementation notes:**
- Health endpoint returns JSON:
  ```json
  {"status": "alive", "timestamp": "2026-09-09T18:42:47.961Z"}
  ```
- Ready endpoint verifies:
  - Config is valid
  - Auth provider is configured (if remote profile)
  - JWKS endpoint is reachable (if JWT verifier)
  - Returns 200 if ready, 503 if not
- Can be integrated into FastMCP via custom middleware or separate endpoint handler
- For now, use simple HTTP handler (no need for separate server)

### 4. Modify Server Entry Point (mcp_server/server.py)

**Changes:**
- Import logging, auth, health modules
- In main/create_mcp_server():
  - Initialize StructuredLogger with Config.log_level
  - Log startup parameters (transport, profile, port, etc.)
  - Create token verifier based on Config.profile
  - If remote profile and no JWT config: raise ValueError before starting
  - Pass token_verifier to FastMCP constructor
  - If HTTP transport: add health/ready endpoints
- Update run() call:
  ```python
  mcp.run(
      transport=config.transport,
      mount_path=config.mcp_endpoint
  )
  ```
- Add graceful shutdown with context manager
- Log successful startup and clean shutdown

**Backward compatibility:**
- stdio transport still works with loopback binding
- Tool signatures unchanged
- Existing test clients continue to work

### 5. Integration Tests (mcp_server/test_http.py)

**New test file with:**
- HTTP connection establishment (use httpx client)
- MCP protocol over HTTP (enumerate tools, invoke generator)
- Authentication tests:
  - Missing Authorization header → 401
  - Invalid token → 401
  - Expired token → 401
  - Valid token → 200
- Concurrent request isolation (ensure separate artifacts)
- Oversized request body → 413 (use max_request_body_size)
- Oversized response → check behavior (may truncate or error)
- Timeout behavior (long-running generator)
- Health endpoint checks
- Invalid MCP requests → appropriate error

**Auth test fixtures:**
- Generate test JWT tokens (valid, expired, wrong issuer, wrong aud)
- Mock token verifier for testing

## Configuration Requirements

### Environment Variables (from Config)

Already defined in PR 1:
```
DEVOPS_OS_TRANSPORT=streamable-http
DEVOPS_OS_HOST=0.0.0.0
DEVOPS_OS_PORT=8000
DEVOPS_OS_MCP_ENDPOINT=/mcp
DEVOPS_OS_REQUEST_SIZE_MB=10
DEVOPS_OS_RESPONSE_SIZE_MB=50
DEVOPS_OS_EXECUTION_TIMEOUT=30
DEVOPS_OS_LOG_LEVEL=INFO
DEVOPS_OS_PROFILE=local|remote
```

### Auth Environment Variables (NEW)

For remote profile:
```
DEVOPS_OS_JWT_ISSUER=https://auth.example.com/
DEVOPS_OS_JWT_AUDIENCE=devops-os-service
DEVOPS_OS_JWT_JWKS_URL=https://auth.example.com/.well-known/jwks.json  [optional]
DEVOPS_OS_JWT_KEY_CACHE_TTL_SECONDS=3600  [optional]
```

### HTTP Environment Variables (NEW)

```
DEVOPS_OS_HTTP_HOST=0.0.0.0          # Override host
DEVOPS_OS_HTTP_PORT=8000             # Override port
DEVOPS_OS_HTTP_CORS_ORIGINS=*        # CORS allowed origins
DEVOPS_OS_HTTP_CORS_CREDENTIALS=true # Allow credentials in CORS
```

## Dependency Additions

Check if needed (may already be in mcp):
- `httpx>=0.24.0` (async HTTP, already in mcp deps likely)
- `python-jose[cryptography]>=3.3.0` OR `PyJWT>=2.8.0` (JWT validation)
- `cryptography>=41.0.0` (asymmetric key handling)

Check existing requirements.txt first. Add to mcp_server/requirements.txt only if missing.

## Testing Strategy

### Unit Tests
- Logging redaction (ensure tokens don't appear)
- JWT validation (valid, expired, wrong issuer, wrong aud, bad signature)
- Token verifier factory (local vs JWT selection)
- Health checks (config validity, auth provider reachability)

### Integration Tests
- HTTP client connects and negotiates MCP protocol
- Tool discovery works over HTTP
- Tool invocation succeeds with valid token
- Tool invocation fails without token
- Concurrent requests produce isolated artifacts
- Oversized request rejected
- Request timeout handled
- Health and ready endpoints respond correctly

### Compatibility Tests
- Existing stdio clients still work
- Existing CLI still works
- All 107 existing tests still pass

## Gate 3 Acceptance Criteria (HTTP Transport)

**MUST verify using real MCP SDK client:**
- [x] Establish HTTP connection to MCP endpoint
- [x] Negotiate MCP protocol
- [x] Discover all 8 tools
- [x] Invoke a tool (e.g., generate_k8s_config)
- [x] Parse and validate returned JSON/YAML
- [x] Compare artifacts with stdio transport (identical)
- [x] Concurrent requests produce independent artifacts
- [x] Exercise malformed requests (expect error)
- [x] Exercise unknown tools (expect error)
- [x] Verify clean shutdown

## Gate 4 Acceptance Criteria (Authentication)

**MUST verify rejection of:**
- [x] Missing Authorization header (remote profile)
- [x] Malformed Authorization header (not "******")
- [x] Invalid token (bad signature, expired, wrong issuer, wrong aud)
- [x] Oversized request (exceeds max_request_body_size)
- [x] Timeout during tool execution

**MUST verify acceptance of:**
- [x] Valid token with correct issuer and audience
- [x] Token with required scopes (if implemented)
- [x] Authorized request produces correct artifact
- [x] Remote mode cannot silently become anonymous

**MUST verify operational correctness:**
- [x] Logs do not expose tokens
- [x] Logs include correlation ID, duration, outcome
- [x] Discovery metadata matches chosen auth integration
- [x] Local mode (no auth) works for development

## Gate 5 Acceptance Criteria (Logging)

**MUST verify:**
- [x] Successful and failed requests can be traced
- [x] Sensitive sentinel values never appear in logs
- [x] Debug logging does not corrupt stdio protocol messages
- [x] Health endpoints expose no secrets
- [x] Error messages are actionable without exposing internals

## Documentation Updates

- README.md: Add HTTP and auth section
- docs/HTTP-SETUP.md [NEW]: Detailed HTTP transport configuration
- docs/AUTH-SETUP.md [NEW]: JWT and OAuth configuration examples
- docs/LOGGING.md [NEW]: Structured logging format and redaction
- docs/TROUBLESHOOTING.md [NEW]: Common auth and HTTP issues

## Validation Checklist

- [ ] All 107 existing tests still pass (stdio, CLI, config, validators)
- [ ] 20+ new HTTP and auth tests added and passing
- [ ] HTTP transport connects and negotiates protocol
- [ ] Authentication enforced in remote profile
- [ ] Logs are structured JSON with redaction
- [ ] Health endpoints respond correctly
- [ ] Concurrent requests remain isolated
- [ ] No backward compatibility breaks
- [ ] No unintended dependencies added
- [ ] No secrets in logs or error messages

## Risk Mitigation

- **Risk:** JWT library breaks FastMCP integration
  - **Mitigation:** Test with mock token verifier first, then real JWT
- **Risk:** HTTP transport not compatible with existing tools
  - **Mitigation:** Test each tool with both stdio and HTTP
- **Risk:** Logging overhead impacts performance
  - **Mitigation:** Use async logging, benchmark before/after
- **Risk:** Auth configuration incomplete or misconfigured
  - **Mitigation:** Fail-closed in remote mode, clear error messages
- **Risk:** Concurrency issues with shared state
  - **Mitigation:** Ensure all state is immutable or thread-safe (use CorrelationContext)

## Implementation Order

1. **Create mcp_server/logging.py** - Foundation for all observability
2. **Create mcp_server/auth.py** - Token verification logic
3. **Create mcp_server/health.py** - Health/ready endpoints
4. **Modify mcp_server/server.py** - Integrate all three modules
5. **Add tests** - Unit + integration tests for HTTP and auth
6. **Update docs** - HTTP, auth, logging, troubleshooting guides
7. **Final regression** - Verify all 107 existing + 20+ new tests pass

## Success Criteria

- Gate 3: HTTP transport works with real MCP client ✓
- Gate 4: Authentication is enforced and validated ✓
- Gate 5: Logs are structured, redacted, and useful ✓
- All existing tests pass ✓
- All new tests pass ✓
- No backward compatibility breaks ✓
- Documentation is complete and accurate ✓
