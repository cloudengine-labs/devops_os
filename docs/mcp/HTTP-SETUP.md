# HTTP Setup Guide

This guide explains how to set up and use the DevOps-OS MCP Server with HTTP transport for ChatGPT Developer mode and web-based MCP clients.

## Quick Start

### Local Development (No Authentication)

Start the HTTP server:

```bash
# Using docker-compose
docker-compose --profile http up mcp-http

# Or using environment variables
export DEVOPS_OS_TRANSPORT=streamable-http
export DEVOPS_OS_HOST=127.0.0.1
export DEVOPS_OS_PORT=8000
python3 -m mcp_server.server
```

The server will be available at `http://127.0.0.1:8000/mcp`

### Verify Server is Running

```bash
# Health check
curl http://127.0.0.1:8000/health

# Readiness check
curl http://127.0.0.1:8000/ready
```

Both endpoints should return JSON with `status: alive` or `ready: true`.

## Configuration

### Environment Variables

All configuration is done via environment variables with the `DEVOPS_OS_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVOPS_OS_TRANSPORT` | `stdio` | Transport type: `stdio`, `sse`, or `streamable-http` |
| `DEVOPS_OS_HOST` | `127.0.0.1` | Bind address for HTTP (loopback by default) |
| `DEVOPS_OS_PORT` | `8000` | HTTP listen port |
| `DEVOPS_OS_MCP_ENDPOINT` | `/mcp` | MCP protocol endpoint path |
| `DEVOPS_OS_PROFILE` | `local` | Security profile: `local` (no auth) or `remote` (requires auth) |
| `DEVOPS_OS_REQUEST_SIZE_MB` | `10` | Maximum request size in MB |
| `DEVOPS_OS_RESPONSE_SIZE_MB` | `50` | Maximum response size in MB |
| `DEVOPS_OS_EXECUTION_TIMEOUT` | `30` | Tool execution timeout in seconds |
| `DEVOPS_OS_LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |

### For Remote Deployment (With Authentication)

Set `DEVOPS_OS_PROFILE=remote` and configure JWT:

```bash
export DEVOPS_OS_PROFILE=remote
export DEVOPS_OS_HOST=0.0.0.0
export DEVOPS_OS_JWT_ISSUER=https://your-issuer/.well-known/openid-configuration
export DEVOPS_OS_JWT_AUDIENCE=your-api-audience
export DEVOPS_OS_JWT_JWKS_URL=https://your-issuer/.well-known/jwks.json
```

See [AUTH-SETUP.md](AUTH-SETUP.md) for detailed authentication configuration.

## Endpoints

### MCP Protocol Endpoint

**Path:** `/mcp` (configurable via `DEVOPS_OS_MCP_ENDPOINT`)

The MCP protocol endpoint handles:
- Tool discovery (list available tools)
- Tool invocation (execute configuration generators)
- Resource requests (retrieve artifacts)

Accepts `Content-Type: application/json` with MCP protocol messages.

### Health Endpoint

**Path:** `/health`

Returns `200 OK` with:

```json
{
  "status": "alive",
  "timestamp": "2026-09-15T17:49:04.772+00:00"
}
```

### Readiness Endpoint

**Path:** `/ready`

Returns `200 OK` when server is ready to accept requests:

```json
{
  "ready": true,
  "checks": {
    "config": "valid",
    "auth": "configured"
  },
  "timestamp": "2026-09-15T17:49:04.772+00:00"
}
```

Returns `503 Service Unavailable` if configuration is invalid or required services are unreachable.

## Request and Response Limits

### Request Size Limits

- **Maximum request body:** 10 MB (configurable via `DEVOPS_OS_REQUEST_SIZE_MB`)
- Includes JSON/MCP protocol messages and any embedded parameters
- Oversized requests return `413 Payload Too Large`

**Justification:** Based on actual artifact measurements:
- Typical tool request: < 5 KB
- 10 MB limit provides 2,000x headroom for batch operations

### Response Size Limits

- **Maximum response body:** 50 MB (configurable via `DEVOPS_OS_RESPONSE_SIZE_MB`)
- Applies to tool output (YAML, JSON, configurations)
- Oversized responses return `413 Payload Too Large`

**Justification:** Based on actual artifact sizes:
- Minimum (K8s manifests): 0.7 KB
- Maximum (SRE configs): 11.4 KB
- 50 MB limit provides 4,400x headroom

If your generator consistently produces large artifacts (> 1 MB), increase this limit:

```bash
export DEVOPS_OS_RESPONSE_SIZE_MB=500  # Allow up to 500 MB responses
```

## Timeout Behavior

### Execution Timeout

- **Default:** 30 seconds per tool invocation
- **Configurable via:** `DEVOPS_OS_EXECUTION_TIMEOUT`

If a tool takes longer than the timeout:
1. HTTP response times out (504 Gateway Timeout)
2. Background generator may continue running (cleanup after completion)
3. Subsequent requests will succeed (server remains operational)

**Best Practice:** Monitor timeout logs to identify slow generators:

```bash
# View timeout events
docker logs devops-os-mcp-http | grep "timeout\|TIMEOUT"
```

### Connection Timeout

HTTP clients should implement their own connection timeout (typically 30-60 seconds).

### Idle Timeout

The MCP protocol enforces a session idle timeout (default: 30 minutes). Long-lived HTTP connections should send periodic keep-alive messages.

## Reverse Proxy Configuration

### Nginx (Local Development)

```nginx
upstream devops-os {
    server localhost:8000;
}

server {
    listen 80;
    server_name localhost;

    location /mcp {
        proxy_pass http://devops-os/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running generators
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }

    location /health {
        proxy_pass http://devops-os/health;
        access_log off;  # Suppress health check logs
    }
}
```

### Nginx (Remote Deployment with Auth)

```nginx
upstream devops-os {
    server devops-os:8000;
}

server {
    listen 443 ssl http2;
    server_name devops-os.example.com;

    ssl_certificate /etc/ssl/certs/devops-os.crt;
    ssl_certificate_key /etc/ssl/private/devops-os.key;

    location /mcp {
        # Authentication verification (with OpenID Connect)
        access_by_lua_file /etc/nginx/auth.lua;
        
        proxy_pass http://devops-os/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        
        # Pass through authorization header
        proxy_set_header Authorization $http_authorization;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }
}
```

### Docker Compose (Behind Nginx)

See example in docker-compose.yml; adjust bind addresses in environment variables:

```bash
DEVOPS_OS_HOST=0.0.0.0  # Listen on all interfaces
DEVOPS_OS_PORT=8000      # Internal port (expose via reverse proxy)
```

## Troubleshooting

### Connection Refused

```
ERROR: Connection refused at 127.0.0.1:8000
```

**Solutions:**
1. Verify server is running: `docker ps` or `ps aux | grep mcp_server`
2. Check port is not in use: `lsof -i :8000`
3. Verify `DEVOPS_OS_HOST` and `DEVOPS_OS_PORT` settings
4. Check firewall rules if accessing remotely

### 503 Service Unavailable (Readiness Failed)

```
GET /ready → 503 Service Unavailable
```

**Solutions:**
1. Check configuration validity: Review environment variables
2. For remote profile: Verify JWT issuer is reachable: `curl https://your-issuer/.well-known/openid-configuration`
3. Check logs: `docker logs devops-os-mcp-http`

### 413 Payload Too Large

```
HTTP/1.1 413 Payload Too Large
```

**Solutions:**
1. Reduce request/response size
2. Increase limits: `export DEVOPS_OS_REQUEST_SIZE_MB=50`
3. Check for very large parameters in tool invocation

### 504 Gateway Timeout

```
HTTP/1.1 504 Gateway Timeout
```

**Solutions:**
1. Increase execution timeout: `export DEVOPS_OS_EXECUTION_TIMEOUT=120`
2. Check if generator is hanging (check logs)
3. Verify no resource constraints (disk space, memory)

## Docker Deployment

Build and run:

```bash
# Build image
docker build -t devops-os-mcp:latest .

# Run with HTTP transport
docker run -d \
  --name devops-os-mcp \
  -e DEVOPS_OS_TRANSPORT=streamable-http \
  -e DEVOPS_OS_HOST=0.0.0.0 \
  -e DEVOPS_OS_PORT=8000 \
  -p 127.0.0.1:8000:8000 \
  devops-os-mcp:latest

# Verify
docker logs devops-os-mcp
curl http://127.0.0.1:8000/health
```

## Performance Considerations

1. **Resource Limits:**
   - Default: 512 MB RAM limit recommended
   - Adjust for your artifact sizes
   - Monitor with: `docker stats devops-os-mcp`

2. **Concurrency:**
   - Default: Unlimited concurrent requests
   - Each request runs in isolated temp directory
   - Monitor with: `docker exec devops-os-mcp ps aux`

3. **Logging:**
   - Structured JSON logs to stderr
   - Use `docker logs --follow` for live monitoring
   - Redirect to external logging service in production

## Next Steps

- See [AUTH-SETUP.md](AUTH-SETUP.md) for JWT authentication configuration
- See [CLIENT-SETUP.md](CLIENT-SETUP.md) for client examples
- See [LOGGING.md](LOGGING.md) for structured logging details
