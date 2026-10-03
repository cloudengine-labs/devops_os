# Client Setup Guide

This guide shows how to connect to the DevOps-OS MCP Server using different clients: command-line, Python SDK, and ChatGPT Developer mode.

## Quick Start

### Local Development (No Authentication)

**Option 1: Using docker-compose**
```bash
# Start HTTP server
docker-compose --profile http up mcp-http

# In another terminal
docker-compose exec mcp-http python3 scripts/smoke-test.py --transport streamable-http
```

**Option 2: Direct execution**
```bash
# Terminal 1: Start server on stdio
python3 -m mcp_server.server

# Terminal 2: Use stdio client (examples below)
```

## Stdio Transport (Command Line)

### Using Python SDK Client

**File:** `examples/stdio-client.py`

```python
#!/usr/bin/env python3
"""
Example: Connect to DevOps-OS MCP Server via stdio transport.

This is the simplest way to test locally. The server runs as a subprocess,
and you communicate via stdin/stdout.
"""

import asyncio
import subprocess
import sys
from mcp import ClientSession
from mcp.client.stdio import StdioClientTransport

async def main():
    # Start server as subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "mcp_server.server"],
        env={"DEVOPS_OS_TRANSPORT": "stdio"},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Create MCP client
    transport = StdioClientTransport(process)
    async with ClientSession(transport) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Found {len(tools.tools)} tools:")
        for tool in tools.tools:
            print(f"  - {tool.name}")
        
        # Call a tool
        result = await session.call_tool(
            "generate_k8s_config",
            {
                "app_name": "my-app",
                "image": "nginx:latest",
                "replicas": 3,
                "port": 80,
                "namespace": "default",
            }
        )
        
        # Print result
        if result.isError:
            print(f"Error: {result.content}")
        else:
            output = result.content[0].text
            print(f"\nGenerated Kubernetes Config ({len(output)} bytes):")
            print(output)

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python3 examples/stdio-client.py
```

## HTTP Transport (Web Client)

### Using Python httpx Library

**File:** `examples/http-client.py`

```python
#!/usr/bin/env python3
"""
Example: Connect to DevOps-OS MCP Server via HTTP transport.

Requires: pip install httpx
"""

import httpx
import json
import sys

# Server configuration
HOST = "127.0.0.1"
PORT = 8000
ENDPOINT = "/mcp"
BASE_URL = f"http://{HOST}:{PORT}"

async def call_mcp_tool(tool_name, arguments):
    """Call a tool via HTTP MCP endpoint."""
    
    # Prepare MCP request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    # Make HTTP request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{ENDPOINT}",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
        return response.json()

async def list_tools():
    """List available tools."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{ENDPOINT}",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()

async def main():
    print(f"Connecting to MCP server at {BASE_URL}{ENDPOINT}")
    
    # Check health
    async with httpx.AsyncClient() as client:
        health = await client.get(f"{BASE_URL}/health")
        print(f"Server health: {health.json()}")
    
    # List tools
    print("\nListing tools...")
    tools_response = await list_tools()
    tools = tools_response.get("result", {}).get("tools", [])
    print(f"Found {len(tools)} tools")
    
    # Call a tool
    print("\nCalling generate_k8s_config...")
    result = await call_mcp_tool(
        "generate_k8s_config",
        {
            "app_name": "my-app",
            "image": "nginx:latest",
            "replicas": 3,
            "port": 80,
            "namespace": "default",
        }
    )
    
    if result:
        output = result.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"\nGenerated config ({len(output)} bytes):")
        print(output[:500] + "..." if len(output) > 500 else output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Run it:**
```bash
# Terminal 1: Start HTTP server
export DEVOPS_OS_TRANSPORT=streamable-http
python3 -m mcp_server.server

# Terminal 2: Run client
python3 examples/http-client.py
```

### Using curl (Debugging)

```bash
# Health check
curl http://127.0.0.1:8000/health

# List tools
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# Call tool
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "generate_k8s_config",
      "arguments": {
        "app_name": "my-app",
        "image": "nginx:latest",
        "replicas": 3,
        "port": 80
      }
    }
  }'
```

## Remote HTTP with Authentication

### Using JWT Token

**File:** `examples/http-client-auth.py`

```python
#!/usr/bin/env python3
"""
Example: Connect to DevOps-OS MCP Server with JWT authentication.

Setup:
1. Configure remote profile on server (see AUTH-SETUP.md)
2. Obtain JWT token from your identity provider
3. Pass token to client
"""

import httpx
import json
import os
import sys

# Configuration
HOST = os.getenv("MCP_HOST", "localhost")
PORT = int(os.getenv("MCP_PORT", 8000))
ENDPOINT = "/mcp"
TOKEN = os.getenv("MCP_TOKEN")  # JWT token from identity provider

BASE_URL = f"https://{HOST}:{PORT}"

if not TOKEN:
    print("ERROR: MCP_TOKEN environment variable not set")
    print("Get a token from your identity provider:")
    print("  TOKEN=$(your-token-script)")
    print("  export MCP_TOKEN=$TOKEN")
    sys.exit(1)

async def call_tool_with_auth(tool_name, arguments):
    """Call a tool with JWT authentication."""
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    # Include authorization header with token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"******"
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f"{BASE_URL}{ENDPOINT}",
            json=request,
            headers=headers
        )
        
        if response.status_code == 401:
            print("ERROR: Authentication failed")
            print("Possible issues:")
            print("  - Token expired (get new one)")
            print("  - Wrong issuer (check configuration)")
            print("  - Wrong audience (check token claims)")
            return None
        
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            print(response.text)
            return None
        
        return response.json()

async def main():
    print(f"Connecting to {BASE_URL}{ENDPOINT} with JWT authentication")
    print(f"Token: {TOKEN[:20]}...")
    
    result = await call_tool_with_auth(
        "generate_k8s_config",
        {
            "app_name": "secure-app",
            "image": "nginx:latest",
            "replicas": 3,
            "port": 443,
            "namespace": "production",
        }
    )
    
    if result:
        output = result.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"Success! Generated {len(output)} bytes")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Run it:**
```bash
# Get token from your provider
TOKEN=$(curl -X POST https://your-issuer/token \
  -d client_id=YOUR_ID \
  -d client_secret=YOUR_SECRET \
  -d audience=devops-os-api \
  -d grant_type=client_credentials | jq -r .access_token)

# Run client
export MCP_TOKEN=$TOKEN
export MCP_HOST=devops-os.example.com
python3 examples/http-client-auth.py
```

## ChatGPT Developer Mode

### Setup

1. **Prerequisites:**
   - ChatGPT Plus subscription
   - DevOps-OS server running with HTTP transport
   - Public HTTPS endpoint (for ChatGPT to reach)
   - Authentication configured (recommended for security)

2. **Step 1: Configure DevOps-OS Server**

   Set up remote profile with authentication:
   ```bash
   export DEVOPS_OS_PROFILE=remote
   export DEVOPS_OS_TRANSPORT=streamable-http
   export DEVOPS_OS_HOST=0.0.0.0
   export DEVOPS_OS_PORT=8000
   export DEVOPS_OS_JWT_ISSUER=https://your-issuer/.well-known/openid-configuration
   export DEVOPS_OS_JWT_AUDIENCE=devops-os-api
   
   python3 -m mcp_server.server
   ```

   Or using docker-compose:
   ```bash
   docker-compose --profile remote up mcp-remote-mock
   ```

   Or behind reverse proxy (Nginx, CloudFlare):
   ```
   https://devops-os.example.com/mcp → http://localhost:8000/mcp
   ```

3. **Step 2: Access ChatGPT Developer Mode**

   - Go to https://chatgpt.com
   - Click "Explore" (top left)
   - Click "Create a GPT"
   - In the builder, go to "Actions" (bottom)

4. **Step 3: Add Custom Action**

   - Click "Create new action"
   - Fill in details:

   ```json
   {
     "name": "DevOps-OS MCP",
     "description": "Generate DevOps configuration (Kubernetes, CI/CD, etc)",
     "server_url": "https://devops-os.example.com"
   }
   ```

5. **Step 4: Configure Authentication (if using remote profile)**

   - Under "Authentication":
     - Type: `OAuth 2.0`
     - Authorization URL: `https://your-issuer/oauth/authorize`
     - Token URL: `https://your-issuer/oauth/token`
     - Client ID: (register with your provider)
     - Scopes: `devops-os:read devops-os:write`

6. **Step 5: Add Schema**

   Click "Schema" and paste:

   ```yaml
   openapi: 3.0.0
   info:
     title: DevOps-OS MCP API
     version: 1.0.0
   paths:
     /mcp:
       post:
         summary: Call MCP tools
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   jsonrpc:
                     type: string
                     example: "2.0"
                   method:
                     type: string
                     enum:
                       - tools/list
                       - tools/call
                   params:
                     type: object
         responses:
           '200':
             description: Success
             content:
               application/json:
                 schema:
                   type: object
   ```

7. **Step 6: Test**

   - Save the GPT
   - Test with prompts like:
     - "Generate a Kubernetes deployment for a Python web app"
     - "Create a GitHub Actions workflow for a Node.js project"
     - "Generate observability configs with SLO targets"

### Example ChatGPT Prompts

Once set up, you can use prompts like:

**Generate Kubernetes Config:**
> "Generate a Kubernetes deployment for my Flask API using the devops-os tool. App name: my-api, image: my-api:v1.0, 3 replicas, port 5000"

**Generate CI/CD Pipeline:**
> "Create a GitHub Actions workflow for a Python/JavaScript project with Kubernetes deployment to Argo CD"

**Generate Observability:**
> "Generate SRE configurations for a service with 99.9% SLO, focusing on latency metrics"

### Troubleshooting ChatGPT Integration

**"Action not responding"**
- Verify HTTPS endpoint is reachable from internet
- Check authentication configuration
- Review server logs for auth failures
- Test with curl: `curl -H "Authorization: ..." https://devops-os.example.com/mcp`

**"Invalid response format"**
- Verify schema is correct OpenAPI
- Check that responses are valid JSON
- Review tool output format

**"Authentication failed"**
- Verify OAuth provider is configured correctly
- Check token claims match DEVOPS_OS_JWT_AUDIENCE
- Verify token is being refreshed correctly

## Testing All Transports

Use the smoke test script to verify all transports:

```bash
# Test stdio
python3 scripts/smoke-test.py --transport stdio

# Test HTTP (server must be running)
python3 scripts/smoke-test.py --transport streamable-http

# With authentication (token required)
export MCP_TOKEN=<your-jwt-token>
python3 scripts/smoke-test.py \
  --transport streamable-http \
  --host devops-os.example.com \
  --port 443
```

## Next Steps

- See [HTTP-SETUP.md](HTTP-SETUP.md) for server configuration
- See [AUTH-SETUP.md](AUTH-SETUP.md) for authentication setup
- See [LOGGING.md](LOGGING.md) for debugging with logs
- See [TROUBLESHOOTING.md](../getting-started/TROUBLESHOOTING.md) for common issues
