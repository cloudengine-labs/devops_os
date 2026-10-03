# Troubleshooting Guide

Common issues and solutions for the DevOps-OS MCP Server.

## Startup Issues

### Port Already in Use

**Error:**
```
ERROR: Address already in use: 0.0.0.0:8000
```

**Causes:**
- Another process is using port 8000
- Previous container didn't shut down cleanly
- Port binding conflict on local machine

**Solutions:**

1. Find and stop the conflicting process:
   ```bash
   # Find process on port 8000
   lsof -i :8000
   
   # Kill it (replace PID with actual process ID)
   kill -9 <PID>
   ```

2. Use a different port:
   ```bash
   export DEVOPS_OS_PORT=8001
   python3 -m mcp_server.server
   ```

3. Clean up Docker containers:
   ```bash
   docker-compose down
   docker rm -f devops-os-mcp-http
   ```

4. Check if service is still running:
   ```bash
   docker ps | grep devops-os-mcp
   docker-compose ps
   ```

### Configuration Errors at Startup

**Error:**
```
ERROR: Configuration error: Missing required field 'JWT_ISSUER'
```

**Causes:**
- Remote profile configured but JWT settings missing
- Invalid environment variable values

**Solutions:**

1. Verify configuration:
   ```bash
   env | grep DEVOPS_OS
   ```

2. For local profile (development):
   ```bash
   export DEVOPS_OS_PROFILE=local
   # No JWT required
   python3 -m mcp_server.server
   ```

3. For remote profile (production), set all JWT variables:
   ```bash
   export DEVOPS_OS_PROFILE=remote
   export DEVOPS_OS_JWT_ISSUER=https://your-issuer/.well-known/openid-configuration
   export DEVOPS_OS_JWT_AUDIENCE=your-audience
   export DEVOPS_OS_JWT_JWKS_URL=https://your-issuer/.well-known/jwks.json
   ```

### JWKS Endpoint Unreachable

**Error:**
```
WARNING: Failed to cache JWKS from https://your-issuer/jwks.json: Connection timeout
```

**Causes:**
- JWKS endpoint is down
- Network connectivity issue
- Firewall blocking requests
- Invalid URL

**Solutions:**

1. Test connectivity to JWKS endpoint:
   ```bash
   curl -v https://your-issuer/.well-known/jwks.json
   ```

2. Verify the URL is correct (check issuer configuration)

3. Check firewall rules:
   ```bash
   # Test DNS resolution
   nslookup your-issuer.example.com
   
   # Test HTTPS connectivity
   openssl s_client -connect your-issuer.example.com:443
   ```

4. Retry with network available (server will cache JWKS on first successful fetch)

## Authentication Issues

### 401 Unauthorized - Missing Token

**Request:**
```bash
curl http://localhost:8000/mcp -d '{"jsonrpc": "2.0", ...}'
```

**Error Response:**
```
HTTP/1.1 401 Unauthorized
```

**Causes:**
- Remote profile enabled but no Authorization header provided
- Token format incorrect

**Solution:**

1. Obtain a token from your identity provider:
   ```bash
   TOKEN=$(curl -X POST https://your-issuer/token \
     -d client_id=YOUR_ID \
     -d client_secret=YOUR_SECRET \
     -d audience=devops-os-api \
     -d grant_type=client_credentials | jq -r .access_token)
   ```

2. Include token in request:
   ```bash
   curl -H "Authorization: ******" \
     http://localhost:8000/mcp \
     -d '{"jsonrpc": "2.0", ...}'
   ```

3. Verify Authorization header format:
   ```bash
   curl -v -H "Authorization: ******" \
     http://localhost:8000/mcp 2>&1 | grep -A5 "Authorization:"
   # Should show: Authorization: ******
   ```

### 401 Unauthorized - Invalid Token Signature

**Logs:**
```
WARNING: Token validation failed: Invalid signature
```

**Causes:**
- Token was signed by different provider
- Token was modified
- Wrong issuer URL configured
- JWKS endpoint returning wrong keys

**Solutions:**

1. Verify token issuer matches configuration:
   ```bash
   # Decode token payload
   python3 -c "
   import base64, json, sys
   token = 'YOUR_TOKEN'
   parts = token.split('.')
   payload = json.loads(base64.urlsafe_b64decode(parts[1]+'=='))
   print('Token Issuer:', payload['iss'])
   print('Token Audience:', payload['aud'])
   print('Token Expiration:', payload['exp'])
   print('Config Audience:', 'DEVOPS_OS_JWT_AUDIENCE')
   "
   ```

2. Regenerate token with correct provider:
   ```bash
   # Get new token from correct issuer
   TOKEN=$(curl -X POST https://YOUR_CORRECT_ISSUER/token ...)
   
   # Test with curl
   curl -H "Authorization: ******" \
     http://localhost:8000/mcp
   ```

3. Verify JWKS endpoint is accessible:
   ```bash
   curl https://your-issuer/.well-known/jwks.json | jq '.keys[0]'
   ```

### 401 Unauthorized - Expired Token

**Logs:**
```
WARNING: Token validation failed: Token has expired
```

**Causes:**
- Token was issued more than its TTL ago
- System clock skew between client and server

**Solutions:**

1. Obtain a fresh token:
   ```bash
   TOKEN=$(curl -X POST https://your-issuer/token \
     -d grant_type=client_credentials \
     -d audience=devops-os-api ...)
   ```

2. Check token expiration:
   ```bash
   python3 -c "
   import json, base64, time
   token = 'YOUR_TOKEN'
   parts = token.split('.')
   payload = json.loads(base64.urlsafe_b64decode(parts[1]+'=='))
   exp = payload['exp']
   now = time.time()
   print(f'Token expires in {exp - now:.0f} seconds')
   print(f'Token valid: {exp > now}')
   "
   ```

3. Sync system clock if needed:
   ```bash
   # Linux
   sudo ntpdate -s time.nist.gov
   
   # Docker container
   docker exec devops-os-mcp ntpdate -s time.nist.gov
   ```

### 401 Unauthorized - Wrong Audience

**Logs:**
```
WARNING: Token validation failed: Token audience doesn't match
```

**Causes:**
- Token created for different API
- `DEVOPS_OS_JWT_AUDIENCE` misconfigured

**Solutions:**

1. Check token audience:
   ```bash
   python3 -c "
   import json, base64
   token = 'YOUR_TOKEN'
   payload = json.loads(base64.urlsafe_b64decode(token.split('.')[1]+'=='))
   print('Token Audience:', payload.get('aud'))
   print('Expected:', 'DEVOPS_OS_JWT_AUDIENCE value')
   "
   ```

2. Update configuration to match token:
   ```bash
   export DEVOPS_OS_JWT_AUDIENCE=<audience-from-token>
   python3 -m mcp_server.server
   ```

3. Or obtain token with correct audience:
   ```bash
   TOKEN=$(curl -X POST https://your-issuer/token \
     -d audience=devops-os-api ...)
   ```

## Tool Validation Issues

### Invalid Input - Kubernetes Identifier

**Error:**
```
ERROR: Validation failed: app_name must match pattern ^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$
```

**Causes:**
- App name contains uppercase letters (K8s requires lowercase)
- App name contains invalid characters
- App name too long (max 63 characters)

**Valid Examples:**
- ✓ `my-app`
- ✓ `app123`
- ✓ `a` (single character)
- ✗ `My-App` (uppercase not allowed)
- ✗ `app_name` (underscore not allowed)
- ✗ `app.name` (dot not allowed)
- ✗ `123app` (can't start with number)

**Solution:**

Use lowercase letters, numbers, and hyphens only:
```bash
# Bad
curl -H "Authorization: ******" \
  http://localhost:8000/mcp \
  -d '{"method": "tools/call", "params": {"name": "generate_k8s_config", "arguments": {"app_name": "My-App"}}}'

# Good
curl -H "Authorization: ******" \
  http://localhost:8000/mcp \
  -d '{"method": "tools/call", "params": {"name": "generate_k8s_config", "arguments": {"app_name": "my-app"}}}'
```

### Invalid Input - Docker Image Reference

**Error:**
```
ERROR: Validation failed: image reference contains invalid characters or format
```

**Causes:**
- Image reference contains shell special characters
- Invalid registry/image format
- Tag contains invalid characters

**Valid Examples:**
- ✓ `my-app:latest`
- ✓ `registry.example.com/my-app:v1.0.0`
- ✓ `gcr.io/project/my-app:sha-abcd1234`
- ✗ `my-app:$(whoami)` (shell substitution)
- ✗ `my-app;&ls` (shell commands)

**Solution:**

Ensure image reference is valid Docker format:
```bash
# Test image validity
docker pull my-app:latest

# Use in tool
curl -H "Authorization: ******" \
  http://localhost:8000/mcp \
  -d '{"method": "tools/call", "params": {"name": "generate_k8s_config", "arguments": {"image": "my-app:latest"}}}'
```

### Invalid Input - Port Number

**Error:**
```
ERROR: Validation failed: port must be between 1 and 65535
```

**Valid Examples:**
- ✓ `8080`
- ✓ `443`
- ✓ `1` (minimum)
- ✓ `65535` (maximum)
- ✗ `0`
- ✗ `70000`
- ✗ `-1`

**Solution:**

Use port between 1 and 65535:
```bash
# Bad
curl ... -d '{"arguments": {"port": 70000}}'

# Good
curl ... -d '{"arguments": {"port": 8080}}'
```

## Generator Issues

### Generator Timeout

**Error:**
```
ERROR: Tool execution timeout after 30 seconds
```

**Causes:**
- Generator is slow (e.g., writing large artifacts)
- Generator is hung or infinite loop
- System resource constraints (disk, memory)

**Solutions:**

1. Increase timeout:
   ```bash
   export DEVOPS_OS_EXECUTION_TIMEOUT=120
   python3 -m mcp_server.server
   ```

2. Check system resources:
   ```bash
   # CPU and memory usage
   docker stats devops-os-mcp-http
   
   # Disk space
   df -h /tmp
   ```

3. Check which generator is slow:
   ```bash
   docker logs devops-os-mcp-http | grep "timeout" | jq '.tool_name'
   ```

4. Investigate generator (if custom):
   - Check for infinite loops
   - Optimize file I/O
   - Consider async/streaming for large outputs

### Generator Output Too Large

**Error:**
```
ERROR: Response size 75 MB exceeds limit 50 MB
```

**Causes:**
- Generator produces large artifacts
- Configuration has many items

**Solutions:**

1. Increase response limit:
   ```bash
   export DEVOPS_OS_RESPONSE_SIZE_MB=200
   python3 -m mcp_server.server
   ```

2. Check generated output:
   ```bash
   # Manually run generator and measure output
   python3 -c "
   from mcp_server.server import generate_sre_configs
   result = generate_sre_configs('my-app', team='platform', slo_type='latency')
   print(f'Output size: {len(result)} bytes')
   "
   ```

3. Optimize inputs (fewer items, less verbose output)

## Server Resource Issues

### Out of Memory (Container)

**Error:**
```
Killed signal: SIGKILL (Docker OOM)
```

**Causes:**
- Generator produces very large artifacts
- Memory leak in generator
- Many concurrent requests without proper cleanup
- Container memory limit too low

**Solutions:**

1. Increase container memory:
   ```bash
   # docker-compose
   services:
     mcp-http:
       mem_limit: 2g
   
   # Or docker run
   docker run --memory 2g devops-os-mcp
   ```

2. Monitor memory usage:
   ```bash
   docker stats devops-os-mcp-http
   ```

3. Reduce concurrent requests (implement rate limiting upstream)

4. Enable swap if available:
   ```bash
   docker run --memory 1g --memory-swap 2g devops-os-mcp
   ```

### Disk Space Issues

**Error:**
```
OSError: No space left on device
```

**Causes:**
- `/tmp` directory full
- Large artifacts accumulating
- Temporary files not cleaned up

**Solutions:**

1. Check available space:
   ```bash
   df -h /tmp
   docker exec devops-os-mcp df -h /tmp
   ```

2. Clean temporary files:
   ```bash
   rm -rf /tmp/devops-os-mcp/*
   docker exec devops-os-mcp rm -rf /tmp/*
   ```

3. Increase `/tmp` space:
   ```bash
   # Create larger tmpfs mount
   docker run --tmpfs /tmp:size=5g devops-os-mcp
   ```

4. Set cleanup policy in docker-compose:
   ```yaml
   tmpfs:
     - /tmp:size=5g,noatime
   ```

## Logging Issues

### No Logs Appearing

**Cause:**
- Logs are on stderr, not stdout
- Docker not capturing stderr
- Log level set too high

**Solution:**

1. Capture stderr:
   ```bash
   # Check stderr specifically
   docker logs -f devops-os-mcp-http 2>&1
   
   # Or redirect stderr to stdout in container
   python3 -m mcp_server.server 2>&1 | tee output.log
   ```

2. Lower log level to see more events:
   ```bash
   export DEVOPS_OS_LOG_LEVEL=DEBUG
   python3 -m mcp_server.server
   ```

3. Verify logging module is working:
   ```bash
   python3 -c "
   from mcp_server.logging import get_logger
   logger = get_logger(__name__, 'INFO')
   logger.log_startup('stdio', 'local')
   "
   ```

## Getting Help

### Collect Debug Information

When reporting issues, include:

```bash
# Environment
env | grep DEVOPS_OS

# Server version and dependencies
pip show mcp pyyaml typer

# Recent logs (with correlation IDs)
docker logs --tail 100 devops-os-mcp-http 2>&1 | tail -50

# System information
docker stats devops-os-mcp-http
df -h
free -h
```

### Report Issues

When reporting issues, include:
1. Error message (full stack trace if available)
2. Environment variables
3. Recent logs with correlation IDs
4. Steps to reproduce
5. Expected vs actual behavior

See [AUTH-SETUP.md](../mcp/AUTH-SETUP.md) and [HTTP-SETUP.md](../mcp/HTTP-SETUP.md) for specific issue categories.
