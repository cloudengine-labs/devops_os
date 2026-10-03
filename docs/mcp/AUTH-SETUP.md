# Authentication Setup Guide

This guide explains how to configure authentication for the DevOps-OS MCP Server for remote deployments.

## Overview

The MCP server supports two security profiles:

### Local Profile (Default)

- **Use for:** Local development, testing, behind a firewall
- **Authentication:** Disabled
- **Authorization:** All requests accepted
- **Binding:** Loopback only (127.0.0.1:8000)
- **Environment:**
  ```bash
  DEVOPS_OS_PROFILE=local
  DEVOPS_OS_HOST=127.0.0.1
  ```

### Remote Profile

- **Use for:** Production, ChatGPT Developer mode, remote access
- **Authentication:** Required (JWT tokens)
- **Authorization:** Tokens validated for issuer, audience, expiration, and scopes
- **Binding:** All interfaces (0.0.0.0) for reverse proxy
- **Environment:**
  ```bash
  DEVOPS_OS_PROFILE=remote
  DEVOPS_OS_HOST=0.0.0.0
  DEVOPS_OS_JWT_ISSUER=https://auth.example.com/.well-known/openid-configuration
  DEVOPS_OS_JWT_AUDIENCE=devops-os-api
  DEVOPS_OS_JWT_JWKS_URL=https://auth.example.com/.well-known/jwks.json
  ```

## Local Profile (Development)

No additional setup required. Just run:

```bash
export DEVOPS_OS_PROFILE=local
export DEVOPS_OS_TRANSPORT=streamable-http
python3 -m mcp_server.server
```

Or with docker-compose:

```bash
docker-compose --profile http up mcp-http
```

### Important: Local Profile Security

- **DO NOT** use local profile in production or over the internet
- **DO NOT** expose local profile on 0.0.0.0 (all interfaces)
- **DO** verify `DEVOPS_OS_HOST=127.0.0.1` (loopback only)

Local profile logs a warning on startup:

```
WARNING: Local profile without authentication - suitable for development only
```

## Remote Profile (Production)

### Step 1: Configure OpenID Connect Provider

The server requires an OpenID Connect (OIDC) compatible identity provider. Common options:

- **Google Cloud:** Google Cloud Identity
- **Microsoft:** Azure AD
- **Auth0:** auth0.com
- **Keycloak:** Open source option
- **Okta:** Enterprise identity
- **GitHub:** GitHub Actions secrets/OpenID Connect

#### Example: Auth0 Setup

1. Go to https://auth0.com and create a new application (Machine to Machine)
2. Note the following values:
   - **Domain:** `your-tenant.auth0.com`
   - **Client ID:** (for your application)
   - **Client Secret:** (secure, not used by server)
3. Configure the application:
   - Name: DevOps-OS MCP Server
   - Identifier: `devops-os-api`

#### Example: Keycloak Setup (Self-Hosted)

1. Create a new Keycloak realm (or use existing)
2. Create a new client for the MCP server
3. Note the following values:
   - **Realm URL:** `https://keycloak.example.com/auth/realms/devops`
   - **Client ID:** `devops-os-server`
   - **JWKS Endpoint:** `https://keycloak.example.com/auth/realms/devops/protocol/openid-connect/certs`

### Step 2: Environment Variables

Configure the MCP server with your provider's values:

```bash
# For Auth0
export DEVOPS_OS_PROFILE=remote
export DEVOPS_OS_JWT_ISSUER=https://your-tenant.auth0.com/.well-known/openid-configuration
export DEVOPS_OS_JWT_AUDIENCE=devops-os-api
export DEVOPS_OS_JWT_JWKS_URL=https://your-tenant.auth0.com/.well-known/jwks.json

# For Keycloak
export DEVOPS_OS_PROFILE=remote
export DEVOPS_OS_JWT_ISSUER=https://keycloak.example.com/auth/realms/devops/.well-known/openid-configuration
export DEVOPS_OS_JWT_AUDIENCE=devops-os-server
export DEVOPS_OS_JWT_JWKS_URL=https://keycloak.example.com/auth/realms/devops/protocol/openid-connect/certs
```

### Step 3: Verify Configuration

Test that the server can reach the JWKS endpoint:

```bash
# Should return a JSON document with "keys" array
curl https://your-issuer/.well-known/jwks.json
```

Start the server:

```bash
python3 -m mcp_server.server
```

Server logs should include:

```
INFO: Remote profile with JWT authentication enabled
INFO: JWKS endpoint configured: https://your-issuer/.well-known/jwks.json
INFO: Listening on 0.0.0.0:8000
```

## JWT Token Format and Validation

### Obtaining a Token

Tokens are obtained from your OpenID Connect provider using client credentials flow (for service-to-service) or authorization code flow (for ChatGPT).

#### Example: Getting a Token from Auth0

```bash
# Service-to-service (use client credentials)
curl --request POST \
  --url https://your-tenant.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "devops-os-api",
    "grant_type": "client_credentials"
  }'

# Returns:
# {
#   "access_token": "******",
#   "token_type": "Bearer",
#   "expires_in": 86400
# }
```

#### Example: Getting a Token from Keycloak

```bash
curl --request POST \
  --url https://keycloak.example.com/auth/realms/devops/protocol/openid-connect/token \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data client_id=devops-os-client \
  --data client_secret=YOUR_CLIENT_SECRET \
  --data grant_type=client_credentials
```

### Token Claims Validation

The server validates the following JWT claims:

| Claim | Validation | Description |
|-------|-----------|-------------|
| `iss` (issuer) | Must match `DEVOPS_OS_JWT_ISSUER` | Ensures token came from trusted provider |
| `aud` (audience) | Must match `DEVOPS_OS_JWT_AUDIENCE` | Ensures token is intended for this API |
| `exp` (expiration) | Must be in the future | Ensures token is not expired |
| `iat` (issued at) | Verifies signature time | Prevents token misuse |
| `signature` | Must be valid with provider's keys | Cryptographic validation |

### Token Payload Example

```json
{
  "iss": "https://your-tenant.auth0.com/",
  "sub": "auth0|abcd1234",
  "aud": "devops-os-api",
  "exp": 1694874843,
  "iat": 1694788443,
  "scope": "devops-os:read devops-os:write"
}
```

## Using Tokens with the MCP Server

### HTTP Requests

Include the token in the `Authorization` header:

```bash
curl -H "Authorization: ******" \
  http://your-server:8000/mcp \
  -d '{"method": "tools/list"}'
```

### MCP SDK Client

Pass token to the client:

```python
from mcp import ClientSession
from mcp.client.sse import SSEClientTransport

# Get token (from your auth provider)
token = get_token()  # Your token acquisition logic

# Create transport with auth
transport = SSEClientTransport(
    url="https://devops-os.example.com/mcp",
    headers={"Authorization": f"******"}
)

# Create session and use normally
async with ClientSession(transport) as session:
    tools = await session.list_tools()
```

### ChatGPT Developer Mode

1. Go to https://chatgpt.com (ChatGPT Plus required)
2. Create a new GPT in "Explore" → "Create a GPT"
3. Configure MCP Server:
   - **Name:** DevOps-OS MCP
   - **Type:** Custom action / OpenAPI
   - **Server URL:** https://devops-os.example.com/mcp
   - **Authentication:** OAuth 2.0 / ******
   - **Token URL:** https://your-issuer/token
   - **Client ID:** (your ChatGPT app registration)
   - **Client Secret:** (from your identity provider)

See [CLIENT-SETUP.md](CLIENT-SETUP.md) for detailed ChatGPT setup.

## Troubleshooting

### Error: Authentication Configuration Error

```
ERROR: Authentication configuration error: Missing JWT issuer
```

**Solution:** Verify `DEVOPS_OS_JWT_ISSUER` is set:

```bash
echo $DEVOPS_OS_JWT_ISSUER
# Should output: https://your-issuer/.well-known/openid-configuration
```

### Error: Token Verification Failed - Invalid Signature

```
ERROR: Token verification failed: Invalid signature
```

**Possible causes:**
1. JWKS endpoint is unreachable
2. Token was issued by different provider
3. Token is malformed

**Solutions:**
1. Verify JWKS endpoint is reachable:
   ```bash
   curl https://your-issuer/.well-known/jwks.json | jq .
   ```

2. Verify token issuer matches configuration:
   ```bash
   # Decode token (jwt.io or cli)
   python3 -c "import base64, json; \
    token='YOUR_TOKEN'; \
    parts=token.split('.'); \
    payload=json.loads(base64.urlsafe_b64decode(parts[1]+'==')); \
    print('Issuer:', payload['iss']); \
    print('Audience:', payload['aud'])"
   ```

3. Regenerate token with correct issuer

### Error: Token Verification Failed - Expired Token

```
ERROR: Token verification failed: Token has expired
```

**Solution:** Obtain a fresh token from your provider

### Error: Access Denied - Wrong Audience

```
ERROR: Access denied - token audience doesn't match
```

**Solution:** Verify token's `aud` claim matches `DEVOPS_OS_JWT_AUDIENCE`:

```bash
# Check token audience
curl -H "Authorization: ******" http://localhost:8000/debug/token 2>/dev/null || echo "Debug endpoint not available"
```

## Security Best Practices

1. **Keep Secrets Secure:**
   - Store `DEVOPS_OS_JWT_ISSUER`, `DEVOPS_OS_JWT_JWKS_URL` in secure configuration
   - Never commit credentials to version control
   - Use environment variables or secure vaults (HashiCorp Vault, AWS Secrets Manager)

2. **Use HTTPS:**
   - Always use `https://` for JWT issuer and JWKS URLs
   - Implement TLS/SSL for all network communication

3. **Token Expiration:**
   - Ensure tokens have reasonable expiration (e.g., 1 hour)
   - Implement token refresh logic in your client

4. **Monitoring:**
   - Log authentication failures (without exposing sensitive data)
   - Alert on repeated failed authentication attempts
   - Monitor JWKS endpoint availability

5. **Scope Validation (Future):**
   - Server currently validates presence of token only
   - Plan to add scope-based authorization in next version
   - Ensure tokens include appropriate scopes for your use case

## Next Steps

- See [HTTP-SETUP.md](HTTP-SETUP.md) for HTTP server configuration
- See [CLIENT-SETUP.md](CLIENT-SETUP.md) for client examples and ChatGPT integration
- See [LOGGING.md](LOGGING.md) for monitoring authentication events
