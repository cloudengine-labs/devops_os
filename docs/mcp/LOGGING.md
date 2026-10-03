# Logging Guide

This guide explains the structured logging system in the DevOps-OS MCP Server, including log format, fields, redaction, and how to use logs for troubleshooting.

## Overview

The MCP server outputs structured JSON logs to stderr, making them easy to parse, filter, and correlate with external logging systems.

### Example Log Entry

```json
{
  "timestamp": "2026-09-15T17:49:04.772+00:00",
  "level": "INFO",
  "correlation_id": "req-abc123def456",
  "message": "Tool invocation completed",
  "tool_name": "generate_k8s_config",
  "transport": "streamable-http",
  "status": "success",
  "duration_ms": 234,
  "output_size_bytes": 4096,
  "error_category": null
}
```

## Log Levels

| Level | Priority | Use For |
|-------|----------|---------|
| DEBUG | 0 (lowest) | Detailed internal state, development troubleshooting |
| INFO | 1 | Normal operation events (startup, tool invocation, shutdown) |
| WARNING | 2 | Unexpected but recoverable conditions |
| ERROR | 3 | Error conditions that may impact functionality |
| CRITICAL | 4 (highest) | Severe errors (misconfiguration, crash scenarios) |

Set the log level via environment variable:

```bash
export DEVOPS_OS_LOG_LEVEL=DEBUG   # Very verbose
export DEVOPS_OS_LOG_LEVEL=INFO    # Default - recommended for production
export DEVOPS_OS_LOG_LEVEL=WARNING  # Only warnings and errors
```

## Log Fields

All logs include these core fields:

### Timestamp
- **Field:** `timestamp`
- **Format:** ISO 8601 UTC (e.g., `2026-09-15T17:49:04.772+00:00`)
- **Purpose:** Precise event timing for correlation

### Log Level
- **Field:** `level`
- **Values:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Purpose:** Filter and search by severity

### Correlation ID
- **Field:** `correlation_id`
- **Format:** `req-` followed by random hex (e.g., `req-abc123def456`)
- **Purpose:** Trace a single request through all system components
- **Lifetime:** Generated at request start, included in all related logs

### Message
- **Field:** `message`
- **Purpose:** Human-readable summary of the event

### Transport
- **Field:** `transport`
- **Values:** `stdio`, `sse`, `streamable-http`
- **Purpose:** Identify which transport the request came from

## Event Types

### Startup Events

**Event:** Server startup
```json
{
  "timestamp": "2026-09-15T17:49:00.123+00:00",
  "level": "INFO",
  "message": "MCP server starting",
  "transport": "streamable-http",
  "profile": "local",
  "host": "127.0.0.1",
  "port": 8000
}
```

### Tool Invocation Events

**Event:** Successful tool invocation
```json
{
  "timestamp": "2026-09-15T17:49:04.772+00:00",
  "level": "INFO",
  "correlation_id": "req-abc123def456",
  "message": "Tool invocation completed",
  "tool_name": "generate_k8s_config",
  "transport": "streamable-http",
  "status": "success",
  "duration_ms": 234,
  "output_size_bytes": 4096,
  "error_category": null
}
```

**Event:** Tool invocation with validation error
```json
{
  "timestamp": "2026-09-15T17:49:05.123+00:00",
  "level": "WARNING",
  "correlation_id": "req-xyz789",
  "message": "Tool invocation failed",
  "tool_name": "generate_k8s_config",
  "transport": "streamable-http",
  "status": "validation_error",
  "duration_ms": 12,
  "error_category": "invalid_input",
  "error_detail": "app_name must match pattern ^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$"
}
```

**Event:** Tool invocation timeout
```json
{
  "timestamp": "2026-09-15T17:49:35.456+00:00",
  "level": "ERROR",
  "correlation_id": "req-timeout123",
  "message": "Tool execution timeout",
  "tool_name": "generate_sre_configs",
  "transport": "streamable-http",
  "status": "timeout",
  "duration_ms": 30001,
  "execution_timeout_seconds": 30,
  "error_category": "execution_timeout"
}
```

### Authentication Events

**Event:** Missing authentication token (remote profile)
```json
{
  "timestamp": "2026-09-15T17:49:06.789+00:00",
  "level": "WARNING",
  "correlation_id": "req-noauth",
  "message": "Authentication required",
  "transport": "streamable-http",
  "status": "auth_required",
  "error_category": "authentication_required"
}
```

**Event:** Invalid token
```json
{
  "timestamp": "2026-09-15T17:49:07.234+00:00",
  "level": "WARNING",
  "correlation_id": "req-badtoken",
  "message": "Token validation failed",
  "transport": "streamable-http",
  "error_category": "auth_failure",
  "failure_reason": "Invalid signature"
}
```

**Event:** Expired token
```json
{
  "timestamp": "2026-09-15T17:49:08.567+00:00",
  "level": "WARNING",
  "correlation_id": "req-expired",
  "message": "Token validation failed",
  "transport": "streamable-http",
  "error_category": "auth_failure",
  "failure_reason": "Token has expired"
}
```

### Shutdown Events

**Event:** Graceful shutdown
```json
{
  "timestamp": "2026-09-15T18:00:00.000+00:00",
  "level": "INFO",
  "message": "MCP server shutting down",
  "uptime_seconds": 600
}
```

## Sensitive Data Redaction

The logger automatically redacts sensitive fields to prevent credential leakage:

### Redacted Fields

The following field names are automatically masked:

- `token`, `access_token`, `refresh_token`
- `password`, `passwd`, `pwd`
- `secret`, `api_secret`, `client_secret`
- `api_key`, `apikey`
- `jwt`, `bearer`
- `signing_key`, `private_key`, `key`
- Any field matching pattern: `.*_token`, `.*_secret`, `.*_key`

### Redaction Marker

Redacted values are replaced with: `<REDACTED_PASSWORD>` or similar

**Example:**

```json
{
  "timestamp": "2026-09-15T17:49:09.012+00:00",
  "level": "DEBUG",
  "message": "Request received",
  "correlation_id": "req-test",
  "authorization_header": "<REDACTED_BEARER>",
  "jwt_token": "<REDACTED_JWT>"
}
```

### Redaction in Tool Parameters

Tool parameters containing secrets are NOT logged by default (only tool name is logged). If you need to debug a specific tool invocation with parameters, use `DEVOPS_OS_LOG_LEVEL=DEBUG` and review separately with proper access controls.

## Using Logs for Troubleshooting

### Finding Related Events

Use correlation ID to find all events for a single request:

```bash
# Using grep
docker logs devops-os-mcp-http | grep "req-abc123def456"

# Using jq (if parsing JSON)
docker logs devops-os-mcp-http | jq 'select(.correlation_id == "req-abc123def456")'

# Using log aggregator (Datadog, ELK Stack, etc.)
filter: correlation_id = "req-abc123def456"
```

### Identifying Common Issues

#### Startup Failure

Look for CRITICAL or ERROR logs with "starting" in the message:

```bash
docker logs devops-os-mcp | jq 'select(.level == "ERROR" and .message | contains("start"))'
```

Output might show:
```json
{
  "level": "ERROR",
  "message": "Configuration error",
  "error_detail": "DEVOPS_OS_JWT_ISSUER is required for remote profile"
}
```

**Solution:** Check [AUTH-SETUP.md](AUTH-SETUP.md) for required environment variables.

#### Authentication Failures

Look for auth_failure error category:

```bash
docker logs devops-os-mcp | jq 'select(.error_category == "auth_failure")'
```

Common issues:
- `failure_reason: "Invalid signature"` → Token from wrong provider
- `failure_reason: "Token has expired"` → Token needs refresh
- `failure_reason: "Wrong audience"` → Token for different API
- `failure_reason: "Wrong issuer"` → Token from unauthorized provider

**Solution:** See [AUTH-SETUP.md](AUTH-SETUP.md) troubleshooting section.

#### Validation Failures

Look for validation_error status:

```bash
docker logs devops-os-mcp | jq 'select(.status == "validation_error")'
```

Includes `error_detail` with specific constraint violation:
- `app_name must match pattern` → Kubernetes identifier rules violated
- `port must be between 1 and 65535` → Port out of range
- `image reference contains invalid characters` → Docker image format error

**Solution:** Fix input according to error_detail message. See tool documentation for accepted values.

#### Timeouts

Look for timeout error category:

```bash
docker logs devops-os-mcp | jq 'select(.error_category == "execution_timeout")'
```

Check:
1. `duration_ms` vs `execution_timeout_seconds` to confirm timeout occurred
2. Which `tool_name` timed out (may indicate slow generator)
3. Increase timeout if needed: `export DEVOPS_OS_EXECUTION_TIMEOUT=60`

**Solution:** 
- Increase timeout for slow operations
- Optimize generator if generating very large artifacts
- Check for resource constraints (disk space, memory)

### Structured Log Analysis

#### Using `jq` Command Line

```bash
# Find all errors in last 1 hour
docker logs devops-os-mcp --since 1h | jq 'select(.level == "ERROR")'

# Count events by status
docker logs devops-os-mcp | jq -s 'group_by(.status) | map({status: .[0].status, count: length})'

# Analyze performance (duration_ms)
docker logs devops-os-mcp | jq 'select(.duration_ms != null) | {tool: .tool_name, duration_ms: .duration_ms}' | jq -s 'sort_by(.duration_ms) | reverse | .[0:5]'  # Top 5 slowest
```

#### Using Log Aggregator (ELK Stack)

```
# Kibana/ElasticSearch query
level: ERROR AND error_category: auth_failure

# Analyze by transport
SELECT transport, COUNT(*) as count FROM logs GROUP BY transport

# Find slow tools (>1 second)
SELECT tool_name, AVG(duration_ms) as avg_duration FROM logs WHERE duration_ms > 1000 GROUP BY tool_name
```

#### Using Datadog

```
# Datadog search query
level:ERROR @error_category:auth_failure

# Dashboard: Errors by category
select: count() by @error_category

# Monitor: Alert on repeated failures
count() > 5 by @tool_name in last 5 minutes
```

## Log Configuration Examples

### Development Environment

```bash
export DEVOPS_OS_LOG_LEVEL=DEBUG
docker-compose --profile http up mcp-http
docker logs --follow devops-os-mcp-http
```

### Production Environment

```bash
export DEVOPS_OS_LOG_LEVEL=INFO
docker run -d \
  -e DEVOPS_OS_LOG_LEVEL=INFO \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=5 \
  devops-os-mcp:latest
```

With log forwarding to external system (e.g., Datadog):

```bash
docker run -d \
  -e DEVOPS_OS_LOG_LEVEL=INFO \
  --log-driver awslogs \
  --log-opt awslogs-group=/ecs/devops-os-mcp \
  --log-opt awslogs-region=us-east-1 \
  devops-os-mcp:latest
```

## Next Steps

- See [HTTP-SETUP.md](HTTP-SETUP.md) for server configuration
- See [TROUBLESHOOTING.md](../getting-started/TROUBLESHOOTING.md) for solutions to common problems
- See [CLIENT-SETUP.md](CLIENT-SETUP.md) for client examples
