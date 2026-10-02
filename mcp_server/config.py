"""Configuration management for DevOps-OS MCP server.

Loads configuration from environment variables (DEVOPS_OS_* prefix)
with sensible defaults for local development.
"""

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Config:
    """MCP server configuration.

    Environment Variables:
    - DEVOPS_OS_TRANSPORT: 'stdio', 'sse', or 'streamable-http' (default: 'stdio')
    - DEVOPS_OS_HOST: Bind address (default: '127.0.0.1')
    - DEVOPS_OS_PORT: Bind port (default: 8000)
    - DEVOPS_OS_MCP_ENDPOINT: MCP HTTP endpoint path (default: '/mcp')
    - DEVOPS_OS_LOG_LEVEL: Logging level (default: 'INFO')
    - DEVOPS_OS_REQUEST_SIZE_MB: Max request body size in MB (default: 10)
    - DEVOPS_OS_RESPONSE_SIZE_MB: Max response body size in MB (default: 50)
    - DEVOPS_OS_EXECUTION_TIMEOUT: Tool execution timeout in seconds (default: 30)
    - DEVOPS_OS_PROFILE: Deployment profile 'local' (no auth) or 'remote' (auth required)
                         (default: 'local')
    - DEVOPS_OS_JWT_ISSUER: JWT issuer URL (required in remote profile)
    - DEVOPS_OS_JWT_AUDIENCE: JWT audience/resource (required in remote profile)
    - DEVOPS_OS_JWT_JWKS_URL: JWKS endpoint URL (optional, derived from issuer if not set)
    - DEVOPS_OS_JWT_ALGORITHMS: Comma-separated JWT algorithms (default: 'RS256,ES256')
    - DEVOPS_OS_ENABLE_SUGGESTIONS: Enable prompt improvement suggestions (default: true)
    - DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD: Minimum confidence level 'high', 'medium', 
                                                  'low' (default: 'medium')
    - DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE: Max suggestions per response (default: 2)
    - DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS: Include example improved prompts (default: true)
    """

    # Transport configuration
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    mcp_endpoint: str = "/mcp"

    # Request/response limits
    request_size_mb: int = 10
    response_size_mb: int = 50
    request_size_bytes: int = field(init=False)
    response_size_bytes: int = field(init=False)

    # Execution configuration
    execution_timeout: int = 30  # seconds
    log_level: str = "INFO"

    # Deployment profile (local or remote)
    profile: Literal["local", "remote"] = "local"

    # Authentication (remote profile)
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_jwks_url: str | None = None
    jwt_algorithms: list[str] = field(default_factory=lambda: ["RS256", "ES256"])
    
    # Prompt improvement suggestions
    enable_suggestions: bool = True
    suggestion_confidence_threshold: str = "medium"  # "high", "medium", "low"
    max_suggestions_per_response: int = 2
    include_examples_in_suggestions: bool = True

    def __post_init__(self):
        """Validate and compute derived values."""
        self.request_size_bytes = self.request_size_mb * 1024 * 1024
        self.response_size_bytes = self.response_size_mb * 1024 * 1024

        # Validate profile-specific requirements
        if self.profile == "remote":
            if not self.jwt_issuer:
                raise ValueError(
                    "DEVOPS_OS_JWT_ISSUER required when DEVOPS_OS_PROFILE=remote"
                )
            if not self.jwt_audience:
                raise ValueError(
                    "DEVOPS_OS_JWT_AUDIENCE required when DEVOPS_OS_PROFILE=remote"
                )

        # Validate port range
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Port must be 1-65535, got {self.port}")

        # Validate size limits (min 1 MB, max 1 GB)
        if not 1 <= self.request_size_mb <= 1024:
            raise ValueError(
                f"DEVOPS_OS_REQUEST_SIZE_MB must be 1-1024, got {self.request_size_mb}"
            )
        if not 1 <= self.response_size_mb <= 1024:
            raise ValueError(
                f"DEVOPS_OS_RESPONSE_SIZE_MB must be 1-1024, got {self.response_size_mb}"
            )

        # Validate timeout (1-600 seconds)
        if not 1 <= self.execution_timeout <= 600:
            raise ValueError(
                f"Execution timeout must be 1-600 seconds, got {self.execution_timeout}"
            )

    @staticmethod
    def from_env() -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config: Configuration object with values from environment

        Raises:
            ValueError: If configuration is invalid
        """
        transport = os.getenv("DEVOPS_OS_TRANSPORT", "stdio")
        if transport not in ("stdio", "sse", "streamable-http"):
            raise ValueError(
                f"DEVOPS_OS_TRANSPORT must be 'stdio', 'sse', or 'streamable-http', got '{transport}'"
            )

        profile = os.getenv("DEVOPS_OS_PROFILE", "local")
        if profile not in ("local", "remote"):
            raise ValueError(
                f"DEVOPS_OS_PROFILE must be 'local' or 'remote', got '{profile}'"
            )

        host = os.getenv("DEVOPS_OS_HOST", "127.0.0.1")
        port = int(os.getenv("DEVOPS_OS_PORT", "8000"))
        mcp_endpoint = os.getenv("DEVOPS_OS_MCP_ENDPOINT", "/mcp")
        log_level = os.getenv("DEVOPS_OS_LOG_LEVEL", "INFO").upper()
        request_size_mb = int(os.getenv("DEVOPS_OS_REQUEST_SIZE_MB", "10"))
        response_size_mb = int(os.getenv("DEVOPS_OS_RESPONSE_SIZE_MB", "50"))
        execution_timeout = int(os.getenv("DEVOPS_OS_EXECUTION_TIMEOUT", "30"))

        jwt_issuer = os.getenv("DEVOPS_OS_JWT_ISSUER")
        jwt_audience = os.getenv("DEVOPS_OS_JWT_AUDIENCE")
        jwt_jwks_url = os.getenv("DEVOPS_OS_JWT_JWKS_URL")
        jwt_algorithms_str = os.getenv("DEVOPS_OS_JWT_ALGORITHMS", "RS256,ES256")
        jwt_algorithms = [a.strip() for a in jwt_algorithms_str.split(",") if a.strip()]
        
        # Prompt improvement suggestions
        enable_suggestions_str = os.getenv("DEVOPS_OS_ENABLE_SUGGESTIONS", "true").lower()
        enable_suggestions = enable_suggestions_str in ("true", "1", "yes")
        
        suggestion_confidence_threshold = os.getenv(
            "DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD", "medium"
        )
        if suggestion_confidence_threshold not in ("high", "medium", "low"):
            raise ValueError(
                f"DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD must be 'high', 'medium', or 'low', "
                f"got '{suggestion_confidence_threshold}'"
            )
        
        max_suggestions_per_response = int(
            os.getenv("DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE", "2")
        )
        if not 1 <= max_suggestions_per_response <= 10:
            raise ValueError(
                f"DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE must be 1-10, got {max_suggestions_per_response}"
            )
        
        include_examples_str = os.getenv("DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS", "true").lower()
        include_examples_in_suggestions = include_examples_str in ("true", "1", "yes")

        return Config(
            transport=transport,
            host=host,
            port=port,
            mcp_endpoint=mcp_endpoint,
            request_size_mb=request_size_mb,
            response_size_mb=response_size_mb,
            execution_timeout=execution_timeout,
            log_level=log_level,
            profile=profile,
            jwt_issuer=jwt_issuer,
            jwt_audience=jwt_audience,
            jwt_jwks_url=jwt_jwks_url,
            jwt_algorithms=jwt_algorithms,
            enable_suggestions=enable_suggestions,
            suggestion_confidence_threshold=suggestion_confidence_threshold,
            max_suggestions_per_response=max_suggestions_per_response,
            include_examples_in_suggestions=include_examples_in_suggestions,
        )
