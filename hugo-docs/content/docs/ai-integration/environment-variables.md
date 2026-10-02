---
title: "Environment Variables Reference"
weight: 25
---

# DevOps-OS MCP: Environment Variables Reference

Complete reference for all environment variables that control DevOps-OS MCP server behavior and features.

---

## Quick Reference

| Variable | Default | Type | Feature |
|----------|---------|------|---------|
| `DEVOPS_OS_TRANSPORT` | `stdio` | string | Communication protocol |
| `DEVOPS_OS_PROFILE` | `local` | string | Deployment profile |
| `DEVOPS_OS_HOST` | `127.0.0.1` | string | HTTP bind address |
| `DEVOPS_OS_PORT` | `8000` | int | HTTP bind port |
| `DEVOPS_OS_MCP_ENDPOINT` | `/mcp` | string | MCP endpoint path |
| `DEVOPS_OS_LOG_LEVEL` | `INFO` | string | Logging verbosity |
| `DEVOPS_OS_REQUEST_SIZE_MB` | `10` | int | Max request size |
| `DEVOPS_OS_RESPONSE_SIZE_MB` | `50` | int | Max response size |
| `DEVOPS_OS_EXECUTION_TIMEOUT` | `30` | int | Tool timeout (seconds) |
| `DEVOPS_OS_MAX_CONCURRENT_CALLS` | `10` | int | Max concurrent tool executions |
| `DEVOPS_OS_JWT_ISSUER` | None | string | JWT issuer URL |
| `DEVOPS_OS_JWT_AUDIENCE` | None | string | JWT audience |
| `DEVOPS_OS_JWT_JWKS_URL` | Auto-derived | string | JWKS endpoint URL |
| `DEVOPS_OS_JWT_ALGORITHMS` | `RS256,ES256` | string | Allowed JWT algorithms |
| `DEVOPS_OS_ENABLE_SUGGESTIONS` | `true` | boolean | Enable prompt suggestions |
| `DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD` | `medium` | string | Suggestion confidence filter |
| `DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE` | `2` | int | Max suggestions |
| `DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS` | `true` | boolean | Include prompt examples |

---

## Transport & Server Configuration

### `DEVOPS_OS_TRANSPORT`

**Type**: String  
**Default**: `stdio`  
**Valid Values**: `stdio`, `sse`, `streamable-http`

Controls how the MCP server communicates with clients.

**Options**:
- **`stdio`** (Standard Input/Output)
  - Use for: Claude Desktop (local)
  - No network exposure
  - Simplest setup
  
- **`streamable-http`** (HTTP with streaming)
  - Use for: Remote deployments, ChatGPT, Docker
  - Network-accessible
  - Requires auth for remote profile

- **`sse`** (Server-Sent Events)
  - Alternative HTTP transport
  - Use for: Specific client requirements

**Example**:
```bash
# Local (Claude Desktop)
export DEVOPS_OS_TRANSPORT=stdio

# Remote (ChatGPT, HTTP)
export DEVOPS_OS_TRANSPORT=streamable-http
```

---

### `DEVOPS_OS_PROFILE`

**Type**: String  
**Default**: `local`  
**Valid Values**: `local`, `remote`

Deployment profile that controls authentication and network binding.

**Options**:
- **`local`** (Development)
  - No authentication
  - Loopback only by default
  - Fast setup for local testing
  
- **`remote`** (Production)
  - Requires JWT authentication
  - Can bind to all interfaces
  - Suitable for shared deployments

**Example**:
```bash
# Development
export DEVOPS_OS_PROFILE=local

# Production (requires JWT configuration)
export DEVOPS_OS_PROFILE=remote
export DEVOPS_OS_JWT_ISSUER=https://auth.example.com/
export DEVOPS_OS_JWT_AUDIENCE=devops-os-service
```

**Related Variables**:
- `DEVOPS_OS_JWT_ISSUER`
- `DEVOPS_OS_JWT_AUDIENCE`
- `DEVOPS_OS_JWT_JWKS_URL`
- `DEVOPS_OS_JWT_ALGORITHMS`

---

## HTTP Server Configuration

> **Only applies when using `DEVOPS_OS_TRANSPORT=streamable-http`**

### `DEVOPS_OS_HOST`

**Type**: String  
**Default**: `127.0.0.1`

IP address the HTTP server binds to.

**Use Cases**:
- `127.0.0.1` - Localhost only (most secure, default)
- `0.0.0.0` - All interfaces (required for Docker/remote access)
- `192.168.1.100` - Specific network interface

**Example**:
```bash
# Bind to all interfaces (for Docker, remote deployment)
export DEVOPS_OS_HOST=0.0.0.0

# Bind to specific interface
export DEVOPS_OS_HOST=192.168.1.100

# Default: localhost only
export DEVOPS_OS_HOST=127.0.0.1
```

**Security Note**: Only use `0.0.0.0` with `DEVOPS_OS_PROFILE=remote` and proper JWT authentication in production.

---

### `DEVOPS_OS_PORT`

**Type**: Integer  
**Default**: `8000`  
**Valid Range**: 1-65535

Port the HTTP server listens on.

**Common Values**:
- `8000` - Default, suitable for development
- `8080` - Alternative HTTP port
- `9000` - Higher port number
- `443` - HTTPS (if running behind proxy)

**Example**:
```bash
# Standard port
export DEVOPS_OS_PORT=8000

# Non-standard (if 8000 is in use)
export DEVOPS_OS_PORT=9000

# With docker compose
export DEVOPS_OS_PORT=8001
```

**Constraint**: When changing ports, ensure firewall rules and proxy configurations are updated accordingly.

---

### `DEVOPS_OS_MCP_ENDPOINT`

**Type**: String  
**Default**: `/mcp`

HTTP path where the MCP server handles requests.

**Use Cases**:
- `/mcp` - Default, simple routing
- `/tools/mcp` - Nested under tools prefix
- `/devops-os` - Application-specific path
- `/api/mcp` - RESTful convention

**Example**:
```bash
# Default
export DEVOPS_OS_MCP_ENDPOINT=/mcp

# Behind a proxy with path prefix
export DEVOPS_OS_MCP_ENDPOINT=/devops-os/mcp

# Nested under tools
export DEVOPS_OS_MCP_ENDPOINT=/tools/mcp
```

**Note**: If running behind a reverse proxy, update your proxy configuration to match this path.

---

## Logging Configuration

### `DEVOPS_OS_LOG_LEVEL`

**Type**: String  
**Default**: `INFO`  
**Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Controls verbosity of server logs (Python logging levels).

**Log Levels** (from most to least verbose):
- **`DEBUG`** - Detailed diagnostic information, variable states, function calls
  - Use for: Troubleshooting issues
  - May include sensitive data
  
- **`INFO`** - General informational messages
  - Use for: Normal operation, monitoring
  - Default level
  
- **`WARNING`** - Warning messages about potential issues
  - Use for: Production (reduced noise)
  
- **`ERROR`** - Error messages only
  - Use for: Critical production systems
  
- **`CRITICAL`** - Only critical failures

**Example**:
```bash
# Development: Maximum detail
export DEVOPS_OS_LOG_LEVEL=DEBUG

# Production: Normal monitoring
export DEVOPS_OS_LOG_LEVEL=INFO

# Production: Warnings only
export DEVOPS_OS_LOG_LEVEL=WARNING
```

**Viewing Logs**:
```bash
# Start server and see logs
export DEVOPS_OS_LOG_LEVEL=DEBUG
python -m mcp_server.server

# Or tail logs if running in background
docker logs -f devops-os-mcp
```

---

## Performance & Resource Tuning

### `DEVOPS_OS_REQUEST_SIZE_MB`

**Type**: Integer  
**Default**: `10`  
**Valid Range**: 1-1024 MB

Maximum size of incoming request body in megabytes.

**Use Cases**:
- `10` - Small/normal prompts (default)
- `50` - Larger prompts with detailed context
- `100` - Very large inputs or batch operations

**Example**:
```bash
# Default: 10 MB
export DEVOPS_OS_REQUEST_SIZE_MB=10

# For large prompt inputs
export DEVOPS_OS_REQUEST_SIZE_MB=50

# For very large inputs (if needed)
export DEVOPS_OS_REQUEST_SIZE_MB=100
```

**When to Increase**:
- Users report "request body too large" errors
- Handling large context windows from AI assistants
- Processing complex multi-config requests

**When to Keep Small**:
- Limited server memory
- Security constraints on input sizes
- Normal use cases

---

### `DEVOPS_OS_RESPONSE_SIZE_MB`

**Type**: Integer  
**Default**: `50`  
**Valid Range**: 1-1024 MB

Maximum size of outgoing response body in megabytes.

**Use Cases**:
- `50` - Standard responses (default)
- `100` - Large generated configurations
- `200` - Multiple large artifacts

**Example**:
```bash
# Default: 50 MB
export DEVOPS_OS_RESPONSE_SIZE_MB=50

# For large generated configs
export DEVOPS_OS_RESPONSE_SIZE_MB=100

# For very large responses
export DEVOPS_OS_RESPONSE_SIZE_MB=200
```

**When to Increase**:
- Generating multiple large Kubernetes manifests
- Creating comprehensive SRE dashboards
- Complex multi-service deployments

**Typical Response Sizes**:
- GitHub Actions workflow: 5-20 KB
- Kubernetes manifests: 10-100 KB
- Prometheus rules: 5-50 KB
- Multiple artifacts: 50-500 KB

---

### `DEVOPS_OS_EXECUTION_TIMEOUT`

**Type**: Integer  
**Default**: `30` seconds  
**Valid Range**: 1-600 seconds

Maximum time a single tool can execute before timing out.

**Use Cases**:
- `30` - Normal tool execution (default)
- `60` - Slower infrastructure
- `120` - Very slow systems
- `300` - Extended timeout for complex operations

**Example**:
```bash
# Default: 30 seconds
export DEVOPS_OS_EXECUTION_TIMEOUT=30

# For slower systems
export DEVOPS_OS_EXECUTION_TIMEOUT=60

# For complex operations
export DEVOPS_OS_EXECUTION_TIMEOUT=120
```

**Common Tool Execution Times**:
- GitHub Actions: 2-5 seconds
- Kubernetes configs: 1-3 seconds
- Jenkins pipelines: 3-8 seconds
- SRE configs: 2-5 seconds

**When to Increase**:
- "Tool execution timeout" errors occur
- Running on slow/limited hardware
- Complex custom scaffolding

**When to Keep Low**:
- Strict SLA requirements
- Limited server resources
- Quick response needed

---

### `DEVOPS_OS_MAX_CONCURRENT_CALLS`

**Type**: Integer  
**Default**: `10`  
**Valid Range**: 1-100

Limits the maximum number of tool executions that can run concurrently. Prevents resource exhaustion and enforces SLA compliance in production.

**Use Cases**:
- `1` - Strictly sequential execution (debugging, very limited resources)
- `5` - Conservative limit (small servers, cost control)
- `10` - Default, balanced for most scenarios
- `20` - High-capacity servers
- `50+` - Large-scale deployments with ample resources

**Example**:
```bash
# Default: 10 concurrent calls
export DEVOPS_OS_MAX_CONCURRENT_CALLS=10

# Limit to 5 for small server
export DEVOPS_OS_MAX_CONCURRENT_CALLS=5

# Allow 20 for high-capacity deployment
export DEVOPS_OS_MAX_CONCURRENT_CALLS=20

# Strict sequential (no concurrency)
export DEVOPS_OS_MAX_CONCURRENT_CALLS=1
```

**When to Lower (1-5)**:
- Limited server CPU/memory
- Cost-constrained deployments
- Strict resource quotas
- Shared infrastructure
- Testing/debugging

**When to Keep Default (10)**:
- Standard deployments
- Most production scenarios
- Balanced performance

**When to Increase (20+)**:
- High-capacity cloud deployments (e.g., Kubernetes)
- High traffic expected
- Ample CPU/memory available
- Auto-scaling infrastructure
- Premium tier deployments

**Production Safety**:
- Set based on available server resources
- Monitor CPU/memory under load
- Start conservative, increase if needed
- Each tool uses ~50-200MB during execution
- Consider: `max_concurrent_calls × avg_tool_memory ≤ available_memory`

**Example Resource Calculation**:
```
Server: 4 CPU, 8GB RAM
Average tool memory: 100MB
Recommended max_concurrent_calls = (8GB × 0.75) / 100MB ≈ 60
But also consider CPU: 4 cores suggests 8-16 concurrent is reasonable
Conservative choice: 10
Aggressive choice: 20
```

---

## Authentication (JWT)

> **Only applies when using `DEVOPS_OS_PROFILE=remote`**

### `DEVOPS_OS_JWT_ISSUER`

**Type**: String  
**Default**: None (required for remote profile)

URL of the JWT token issuer.

**Common Issuers**:
- `https://auth.example.com/` - Custom auth server
- `https://accounts.google.com/` - Google OAuth
- `https://login.microsoftonline.com/` - Azure AD
- `https://github.com/login/oauth/` - GitHub OAuth

**Example**:
```bash
# Custom auth server
export DEVOPS_OS_JWT_ISSUER=https://auth.company.com/

# Google
export DEVOPS_OS_JWT_ISSUER=https://accounts.google.com/

# Azure AD
export DEVOPS_OS_JWT_ISSUER=https://login.microsoftonline.com/YOUR_TENANT_ID/
```

**Related Variables**:
- `DEVOPS_OS_JWT_AUDIENCE` - Must match token's 'aud' claim
- `DEVOPS_OS_JWT_JWKS_URL` - Auto-derived if not set

---

### `DEVOPS_OS_JWT_AUDIENCE`

**Type**: String  
**Default**: None (required for remote profile)

Expected JWT audience claim value. The token's `aud` claim must match this value.

**Format**: Usually a resource identifier or application name.

**Example**:
```bash
# Application identifier
export DEVOPS_OS_JWT_AUDIENCE=devops-os-service

# API resource
export DEVOPS_OS_JWT_AUDIENCE=api://devops-os

# Custom identifier
export DEVOPS_OS_JWT_AUDIENCE=urn:devops-os:mcp
```

**Verification**: Tokens without matching audience will be rejected.

---

### `DEVOPS_OS_JWT_JWKS_URL`

**Type**: String  
**Default**: Auto-derived from `DEVOPS_OS_JWT_ISSUER`

URL of the JWKS (JSON Web Key Set) endpoint for token validation.

**Auto-Derivation**:
If not set, derived by appending `/.well-known/jwks.json` to the issuer URL.

Example:
- Issuer: `https://auth.example.com/`
- Auto-derived: `https://auth.example.com/.well-known/jwks.json`

**Example**:
```bash
# Let it auto-derive (recommended)
export DEVOPS_OS_JWT_ISSUER=https://auth.example.com/
# Automatically: JWKS URL = https://auth.example.com/.well-known/jwks.json

# Explicit JWKS URL (if auto-derivation doesn't work)
export DEVOPS_OS_JWT_JWKS_URL=https://auth.example.com/oauth/jwks
```

**When to Set Explicitly**:
- Non-standard JWKS endpoint path
- Different domain for JWKS vs issuer
- Proxy or custom configuration

---

### `DEVOPS_OS_JWT_ALGORITHMS`

**Type**: String (comma-separated)  
**Default**: `RS256,ES256`

Allowed JWT signing algorithms.

**Common Algorithms**:
- `RS256` - RSA with SHA-256 (most common)
- `ES256` - ECDSA with SHA-256
- `HS256` - HMAC with SHA-256
- `RS512` - RSA with SHA-512

**Example**:
```bash
# Default: Both RSA and ECDSA
export DEVOPS_OS_JWT_ALGORITHMS=RS256,ES256

# RSA only (most common)
export DEVOPS_OS_JWT_ALGORITHMS=RS256

# Multiple algorithms
export DEVOPS_OS_JWT_ALGORITHMS=RS256,RS512,ES256

# HMAC (less common, not recommended for server signing)
export DEVOPS_OS_JWT_ALGORITHMS=HS256
```

**Security Note**: Restrict to algorithms your auth provider actually uses to prevent downgrade attacks.

---

## Prompt Improvement Suggestions

### `DEVOPS_OS_ENABLE_SUGGESTIONS`

**Type**: Boolean  
**Default**: `true`  
**Valid Values**: `true`, `false`, `1`, `0`, `yes`, `no`

Enable or disable prompt improvement suggestion feature.

**Example**:
```bash
# Enable suggestions (default)
export DEVOPS_OS_ENABLE_SUGGESTIONS=true

# Disable suggestions
export DEVOPS_OS_ENABLE_SUGGESTIONS=false

# Alternative formats
export DEVOPS_OS_ENABLE_SUGGESTIONS=1      # enabled
export DEVOPS_OS_ENABLE_SUGGESTIONS=0      # disabled
```

**What Suggestions Do**:
- Analyze user prompts for specificity
- Detect missing required parameters
- Suggest improvements for better outputs
- Provide examples of improved prompts

**When to Disable**:
- Strictly minimal responses needed
- Integration with systems that can't handle JSON
- Lower latency required (small overhead when enabled)

---

### `DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD`

**Type**: String  
**Default**: `medium`  
**Valid Values**: `high`, `medium`, `low`

Minimum confidence level for suggestions to display.

**Confidence Levels**:
- **`high`** - Only critical gaps
- **`medium`** - Important gaps (balanced, recommended default)
- **`low`** - All suggestions including minor improvements

**Example**:
```bash
# Show only high-confidence suggestions
export DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD=high

# Show medium and high (default, balanced)
export DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD=medium

# Show all suggestions
export DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD=low
```

**Selection Guide**:
- `high` - For production, reduce noise
- `medium` - Standard use, good balance
- `low` - Learning/exploration mode

---

### `DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE`

**Type**: Integer  
**Default**: `2`  
**Valid Range**: 1-10

Maximum number of suggestions to include per response.

**Example**:
```bash
# Default: 2 suggestions
export DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=2

# Show only 1 suggestion
export DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=1

# Show up to 3 suggestions
export DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=3
```

**Balancing**:
- `1` - Minimal, show most critical suggestion only
- `2` - Balanced (default)
- `3+` - Comprehensive guidance

---

### `DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS`

**Type**: Boolean  
**Default**: `true`  
**Valid Values**: `true`, `false`, `1`, `0`, `yes`, `no`

Include example improved prompts in suggestions.

**Example**:
```bash
# Include examples (default)
export DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS=true

# Exclude examples (shorter responses)
export DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS=false
```

**When to Disable**:
- Minimal response size needed
- Using with systems sensitive to response length
- Faster parsing preferred

**When to Enable**:
- Users learning how to improve prompts
- Interactive chatbot scenario
- Educational use

---

## Configuration Examples

### Local Development (Claude Desktop)

```bash
# Minimal configuration
export DEVOPS_OS_TRANSPORT=stdio
export DEVOPS_OS_PROFILE=local
export DEVOPS_OS_LOG_LEVEL=INFO

python -m mcp_server.server
```

### Docker Local (HTTP, no auth)

```bash
export DEVOPS_OS_TRANSPORT=streamable-http
export DEVOPS_OS_PROFILE=local
export DEVOPS_OS_HOST=0.0.0.0
export DEVOPS_OS_PORT=8000
export DEVOPS_OS_LOG_LEVEL=INFO

python -m mcp_server.server
```

### Remote Production (ChatGPT, JWT auth)

```bash
export DEVOPS_OS_TRANSPORT=streamable-http
export DEVOPS_OS_PROFILE=remote
export DEVOPS_OS_HOST=0.0.0.0
export DEVOPS_OS_PORT=8000
export DEVOPS_OS_JWT_ISSUER=https://auth.example.com/
export DEVOPS_OS_JWT_AUDIENCE=devops-os-service
export DEVOPS_OS_LOG_LEVEL=WARNING
export DEVOPS_OS_EXECUTION_TIMEOUT=60

python -m mcp_server.server
```

### Performance Tuned (Large configurations)

```bash
export DEVOPS_OS_TRANSPORT=streamable-http
export DEVOPS_OS_REQUEST_SIZE_MB=100
export DEVOPS_OS_RESPONSE_SIZE_MB=200
export DEVOPS_OS_EXECUTION_TIMEOUT=120
export DEVOPS_OS_LOG_LEVEL=INFO

python -m mcp_server.server
```

### Debug Mode (Troubleshooting)

```bash
export DEVOPS_OS_LOG_LEVEL=DEBUG
export DEVOPS_OS_EXECUTION_TIMEOUT=120
export DEVOPS_OS_ENABLE_SUGGESTIONS=true
export DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD=low
export DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=5

python -m mcp_server.server
```

---

## Docker Compose Example

```yaml
version: '3.8'

services:
  devops-os:
    image: devops-os-mcp:latest
    environment:
      DEVOPS_OS_TRANSPORT: streamable-http
      DEVOPS_OS_PROFILE: remote
      DEVOPS_OS_HOST: 0.0.0.0
      DEVOPS_OS_PORT: 8000
      DEVOPS_OS_JWT_ISSUER: https://auth.example.com/
      DEVOPS_OS_JWT_AUDIENCE: devops-os-service
      DEVOPS_OS_LOG_LEVEL: INFO
      DEVOPS_OS_REQUEST_SIZE_MB: 50
      DEVOPS_OS_RESPONSE_SIZE_MB: 100
      DEVOPS_OS_EXECUTION_TIMEOUT: 60
    ports:
      - "8000:8000"
    restart: unless-stopped
```

---

## Environment Variable Loading

DevOps-OS MCP loads variables in this priority order:

1. **Explicitly set environment variables** (highest priority)
2. **`.env` file** (if present in working directory)
3. **Built-in defaults** (lowest priority)

### Using a `.env` File

Create `.env` file:
```bash
DEVOPS_OS_TRANSPORT=streamable-http
DEVOPS_OS_PROFILE=remote
DEVOPS_OS_JWT_ISSUER=https://auth.example.com/
DEVOPS_OS_JWT_AUDIENCE=devops-os-service
```

Load and run:
```bash
set -a
source .env
set +a
python -m mcp_server.server
```

---

## Validation & Constraints

| Variable | Constraints | Error Example |
|----------|-------------|----------------|
| `DEVOPS_OS_TRANSPORT` | Must be: `stdio`, `sse`, `streamable-http` | Invalid transport 'http' |
| `DEVOPS_OS_PROFILE` | Must be: `local` or `remote` | Invalid profile 'staging' |
| `DEVOPS_OS_PORT` | Integer between 1-65535 | Port must be 1-65535 |
| `DEVOPS_OS_REQUEST_SIZE_MB` | Integer 1-1024 | Must be 1-1024 |
| `DEVOPS_OS_RESPONSE_SIZE_MB` | Integer 1-1024 | Must be 1-1024 |
| `DEVOPS_OS_EXECUTION_TIMEOUT` | Integer 1-600 | Must be 1-600 seconds |
| `DEVOPS_OS_MAX_CONCURRENT_CALLS` | Integer 1-100 | Must be 1-100 |
| `DEVOPS_OS_LOG_LEVEL` | Valid Python log level | Must be valid level |
| `DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD` | `high`, `medium`, or `low` | Invalid threshold |
| `DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE` | Integer 1-10 | Must be 1-10 |

---

## Troubleshooting

### "Configuration error: Port must be 1-65535"
- Check `DEVOPS_OS_PORT` is a valid port number
- Ensure no letters or special characters

### "Invalid profile: remote" with missing JWT
- When using `DEVOPS_OS_PROFILE=remote`, both `DEVOPS_OS_JWT_ISSUER` and `DEVOPS_OS_JWT_AUDIENCE` are required
- Set both variables before starting server

### "Tool execution timeout" errors
- Increase `DEVOPS_OS_EXECUTION_TIMEOUT`
- Check server system resources
- Verify network latency

### Request/Response size errors
- Increase `DEVOPS_OS_REQUEST_SIZE_MB` for large inputs
- Increase `DEVOPS_OS_RESPONSE_SIZE_MB` for large outputs
- Check server available memory

### "Bind address already in use"
- Change `DEVOPS_OS_PORT` to unused port
- Or stop other process using same port
- Check with: `lsof -i :8000`

---

## See Also

- [MCP Setup & Configuration Guide](mcp-setup.md)
- [Prompt Improvement Suggestions](../../../PROMPT_SUGGESTIONS.md)
