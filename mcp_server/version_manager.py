"""
DevOps-OS Version Manager for Dev Containers

Manages programming language and tool versions via environment variables with
security-aware suggestions and update recommendations. Supports:

- Version tracking with default, LTS, and latest versions
- Security advisory database for known vulnerabilities
- Version comparison and constraint validation
- Environment variable persistence (.env files)
- Automatic security update suggestions
- Version status tracking (stable, deprecated, EOL)

Example:
    >>> from mcp_server.version_manager import VersionManager
    >>> vm = VersionManager()
    >>> versions = vm.get_versions(['python', 'go', 'node'])
    >>> updates = vm.get_security_updates(['python'])
    >>> vm.save_env_file('.env', versions)
"""

import os
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from packaging import version as pkg_version


# ============================================================================
# Version Database with Security Information
# ============================================================================

VERSION_DATABASE = {
    # Programming Languages
    "python": {
        "default": "3.12",
        "lts": ["3.12", "3.11", "3.10"],
        "latest": "3.13",
        "supported": [
            {"version": "3.13", "status": "latest", "security": "stable", "eol": "2029-10"},
            {"version": "3.12", "status": "lts", "security": "stable", "eol": "2028-10"},
            {"version": "3.11", "status": "stable", "security": "stable", "eol": "2027-10"},
            {"version": "3.10", "status": "stable", "security": "stable", "eol": "2026-10"},
            {"version": "3.9", "status": "deprecated", "security": "deprecated", "eol": "2025-10"},
            {"version": "3.8", "status": "eol", "security": "critical", "eol": "2024-10"},
        ],
    },
    "java": {
        "default": "21",
        "lts": ["21", "17", "11"],
        "latest": "23",
        "supported": [
            {"version": "23", "status": "latest", "security": "stable", "eol": "2025-09"},
            {"version": "21", "status": "lts", "security": "stable", "eol": "2031-09"},
            {"version": "17", "status": "lts", "security": "stable", "eol": "2029-09"},
            {"version": "11", "status": "lts", "security": "stable", "eol": "2026-09"},
            {"version": "8", "status": "eol", "security": "critical", "eol": "2022-12"},
        ],
    },
    "go": {
        "default": "1.25.0",
        "lts": ["1.25.0", "1.24.0"],
        "latest": "1.25.0",
        "supported": [
            {"version": "1.25.0", "status": "latest", "security": "stable", "eol": "2026-08"},
            {"version": "1.24.0", "status": "stable", "security": "stable", "eol": "2025-12"},
            {"version": "1.23.0", "status": "stable", "security": "stable", "eol": "2025-08"},
            {"version": "1.22.0", "status": "deprecated", "security": "deprecated", "eol": "2025-02"},
            {"version": "1.21.0", "status": "deprecated", "security": "deprecated", "eol": "2024-08"},
        ],
    },
    "node": {
        "default": "22",
        "lts": ["22", "20", "18"],
        "latest": "23",
        "supported": [
            {"version": "23", "status": "latest", "security": "stable", "eol": "2025-06"},
            {"version": "22", "status": "lts", "security": "stable", "eol": "2027-04"},
            {"version": "20", "status": "lts", "security": "stable", "eol": "2026-04"},
            {"version": "18", "status": "lts", "security": "stable", "eol": "2025-04"},
            {"version": "16", "status": "eol", "security": "critical", "eol": "2023-11"},
        ],
    },
    "rust": {
        "default": "1.81.0",
        "lts": ["1.81.0"],
        "latest": "1.81.0",
        "supported": [
            {"version": "1.81.0", "status": "latest", "security": "stable", "eol": "2026-01"},
            {"version": "1.80.0", "status": "stable", "security": "stable", "eol": "2025-12"},
            {"version": "1.79.0", "status": "stable", "security": "stable", "eol": "2025-10"},
            {"version": "1.78.0", "status": "stable", "security": "deprecated", "eol": "2025-09"},
        ],
    },
    "ruby": {
        "default": "3.3",
        "lts": ["3.3", "3.2"],
        "latest": "3.4",
        "supported": [
            {"version": "3.4", "status": "latest", "security": "stable", "eol": "2027-12"},
            {"version": "3.3", "status": "lts", "security": "stable", "eol": "2027-03"},
            {"version": "3.2", "status": "stable", "security": "stable", "eol": "2026-03"},
            {"version": "3.1", "status": "deprecated", "security": "deprecated", "eol": "2025-12"},
            {"version": "3.0", "status": "eol", "security": "critical", "eol": "2024-12"},
        ],
    },
    # CI/CD and Container Tools
    "docker": {
        "default": "27.0.0",
        "lts": ["27.0.0", "26.0.0"],
        "latest": "27.0.0",
        "supported": [
            {"version": "27.0.0", "status": "latest", "security": "stable", "eol": "2026-06"},
            {"version": "26.0.0", "status": "stable", "security": "stable", "eol": "2025-12"},
            {"version": "25.0.0", "status": "stable", "security": "deprecated", "eol": "2025-06"},
            {"version": "24.0.0", "status": "deprecated", "security": "deprecated", "eol": "2024-12"},
        ],
    },
    # Kubernetes and GitOps Tools
    "kubectl": {
        "default": "1.31.0",
        "lts": ["1.31.0", "1.30.0"],
        "latest": "1.31.0",
        "supported": [
            {"version": "1.31.0", "status": "latest", "security": "stable", "eol": "2025-06"},
            {"version": "1.30.0", "status": "stable", "security": "stable", "eol": "2025-04"},
            {"version": "1.29.0", "status": "stable", "security": "stable", "eol": "2025-02"},
            {"version": "1.28.0", "status": "deprecated", "security": "deprecated", "eol": "2024-11"},
        ],
    },
    "helm": {
        "default": "3.16.0",
        "lts": ["3.16.0", "3.15.0"],
        "latest": "3.16.0",
        "supported": [
            {"version": "3.16.0", "status": "latest", "security": "stable", "eol": "2026-12"},
            {"version": "3.15.0", "status": "stable", "security": "stable", "eol": "2026-10"},
            {"version": "3.14.0", "status": "stable", "security": "stable", "eol": "2026-08"},
            {"version": "3.13.0", "status": "deprecated", "security": "deprecated", "eol": "2026-05"},
        ],
    },
    "terraform": {
        "default": "1.9.0",
        "lts": ["1.9.0", "1.8.0"],
        "latest": "1.9.0",
        "supported": [
            {"version": "1.9.0", "status": "latest", "security": "stable", "eol": "2026-12"},
            {"version": "1.8.0", "status": "stable", "security": "stable", "eol": "2026-08"},
            {"version": "1.7.0", "status": "stable", "security": "deprecated", "eol": "2026-04"},
            {"version": "1.6.0", "status": "deprecated", "security": "deprecated", "eol": "2025-12"},
        ],
    },
    "prometheus": {
        "default": "3.5.1",
        "lts": ["3.5.1", "3.4.0"],
        "latest": "3.5.1",
        "supported": [
            {"version": "3.5.1", "status": "latest", "security": "stable", "eol": "2026-12"},
            {"version": "3.4.0", "status": "stable", "security": "stable", "eol": "2026-06"},
            {"version": "3.3.0", "status": "deprecated", "security": "deprecated", "eol": "2025-12"},
            {"version": "2.50.0", "status": "eol", "security": "critical", "eol": "2024-01"},
        ],
    },
    "grafana": {
        "default": "12.4.2",
        "lts": ["12.4.2", "11.5.0"],
        "latest": "12.4.2",
        "supported": [
            {"version": "12.4.2", "status": "latest", "security": "stable", "eol": "2026-12"},
            {"version": "11.5.0", "status": "stable", "security": "stable", "eol": "2026-06"},
            {"version": "10.4.0", "status": "deprecated", "security": "deprecated", "eol": "2025-12"},
            {"version": "9.5.0", "status": "eol", "security": "critical", "eol": "2024-01"},
        ],
    },
}

# Environment variable prefix for version configuration
ENV_PREFIX = "DEVOPS_OS_VERSION_"


# ============================================================================
# Version Manager Class
# ============================================================================

class VersionManager:
    """Manages tool/language versions with security awareness and env var support."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize version manager.

        Args:
            env_file: Optional path to .env file for version persistence
        """
        self.env_file = env_file
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict[str, str]:
        """Load versions from environment variables or .env file."""
        versions = {}

        # Load from .env file if specified
        if self.env_file and os.path.exists(self.env_file):
            with open(self.env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key.startswith(ENV_PREFIX):
                            tool = key[len(ENV_PREFIX):].lower()
                            versions[tool] = value.strip()

        # Load from environment variables (takes precedence)
        for tool in VERSION_DATABASE.keys():
            env_var = f"{ENV_PREFIX}{tool.upper()}"
            if env_var in os.environ:
                versions[tool] = os.environ[env_var]
            elif tool not in versions:
                # Use default version if not set
                versions[tool] = VERSION_DATABASE[tool]["default"]

        return versions

    def get_versions(self, tools: Optional[List[str]] = None) -> Dict[str, str]:
        """Get current versions for specified tools or all known tools."""
        if tools is None:
            return self.versions.copy()

        result = {}
        for tool in tools:
            if tool in self.versions:
                result[tool] = self.versions[tool]
            elif tool in VERSION_DATABASE:
                result[tool] = VERSION_DATABASE[tool]["default"]
        return result

    def get_version_info(self, tool: str) -> Optional[Dict[str, Any]]:
        """Get version info for a specific tool."""
        if tool not in VERSION_DATABASE:
            return None

        current_version = self.versions.get(tool, VERSION_DATABASE[tool]["default"])
        db = VERSION_DATABASE[tool]

        # Find current version info
        current_info = None
        for v in db["supported"]:
            if v["version"] == current_version:
                current_info = v
                break

        return {
            "tool": tool,
            "current": current_version,
            "default": db["default"],
            "latest": db["latest"],
            "lts": db["lts"],
            "info": current_info or {"version": current_version, "status": "unknown"},
            "all_versions": db["supported"],
        }

    def check_version_updates(self, tools: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Check for available updates for tools."""
        if tools is None:
            tools = list(VERSION_DATABASE.keys())

        updates = {}
        for tool in tools:
            if tool not in VERSION_DATABASE:
                continue

            info = self.get_version_info(tool)
            current = pkg_version.parse(self._normalize_version(info["current"]))
            latest = pkg_version.parse(self._normalize_version(info["latest"]))
            lts_versions = [pkg_version.parse(self._normalize_version(v)) for v in info["lts"]]

            updates[tool] = {
                "tool": tool,
                "current": info["current"],
                "latest": info["latest"],
                "can_update": latest > current,
                "can_update_lts": any(v > current for v in lts_versions),
                "status": info["info"]["status"],
                "security_level": info["info"]["security"],
            }

        return updates

    def get_security_updates(self, tools: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Get security-critical updates for tools."""
        if tools is None:
            tools = list(VERSION_DATABASE.keys())

        security_updates = {}
        for tool in tools:
            if tool not in VERSION_DATABASE:
                continue

            info = self.get_version_info(tool)
            current_security = info["info"]["security"]

            # Check if current version has security issues
            if current_security in ["critical", "high", "deprecated"]:
                # Find latest safe version
                latest_safe = None
                for v in info["all_versions"]:
                    if v["security"] == "stable":
                        if latest_safe is None or pkg_version.parse(
                            self._normalize_version(v["version"])
                        ) > pkg_version.parse(self._normalize_version(latest_safe["version"])):
                            latest_safe = v

                if latest_safe and latest_safe["version"] != info["current"]:
                    security_updates[tool] = {
                        "tool": tool,
                        "current": info["current"],
                        "current_security": current_security,
                        "recommended": latest_safe["version"],
                        "urgency": self._calculate_urgency(current_security),
                        "reason": f"Current version has {current_security} security issues",
                    }

        return security_updates

    def suggest_versions(
        self, tools: Optional[List[str]] = None, prefer_lts: bool = False
    ) -> Dict[str, str]:
        """Suggest recommended versions for tools."""
        if tools is None:
            tools = list(VERSION_DATABASE.keys())

        suggestions = {}
        for tool in tools:
            if tool not in VERSION_DATABASE:
                continue

            db = VERSION_DATABASE[tool]
            if prefer_lts:
                suggestions[tool] = db["lts"][0]  # First LTS is latest stable LTS
            else:
                suggestions[tool] = db["latest"]

        return suggestions

    def set_version(self, tool: str, version: str) -> bool:
        """Set version for a tool."""
        if tool not in VERSION_DATABASE:
            return False

        # Validate version exists
        valid_versions = [v["version"] for v in VERSION_DATABASE[tool]["supported"]]
        if version not in valid_versions:
            # Try partial match for versions like "1.x" or "3.x"
            if not any(v.startswith(version.rstrip(".x")) for v in valid_versions):
                return False

        self.versions[tool] = version
        return True

    def save_env_file(self, filepath: str, versions: Optional[Dict[str, str]] = None) -> bool:
        """Save versions to a .env file."""
        if versions is None:
            versions = self.versions

        try:
            with open(filepath, "w") as f:
                f.write("# DevOps-OS Version Configuration\n")
                f.write("# Auto-generated by VersionManager\n\n")
                for tool, version in sorted(versions.items()):
                    f.write(f"{ENV_PREFIX}{tool.upper()}={version}\n")
            return True
        except Exception:
            return False

    def save_env_vars(self, versions: Optional[Dict[str, str]] = None) -> None:
        """Save versions to environment variables."""
        if versions is None:
            versions = self.versions

        for tool, version in versions.items():
            os.environ[f"{ENV_PREFIX}{tool.upper()}"] = version

    @staticmethod
    def _normalize_version(version_str: str) -> str:
        """Normalize version string for comparison."""
        if version_str == "latest":
            return "999.999.999"
        # Handle versions like "1.25.0"
        parts = version_str.split(".")
        # Pad with zeros for consistent comparison
        while len(parts) < 3:
            parts.append("0")
        return ".".join(parts[:3])

    @staticmethod
    def _calculate_urgency(security_level: str) -> str:
        """Calculate urgency based on security level."""
        if security_level == "critical":
            return "critical"
        elif security_level == "high":
            return "high"
        elif security_level == "deprecated":
            return "medium"
        else:
            return "low"


def get_version_suggestions(
    tools: List[str], include_security: bool = True, prefer_lts: bool = False
) -> Dict[str, Any]:
    """
    Get version suggestions for tools with optional security awareness.

    Args:
        tools: List of tool names
        include_security: Include security update suggestions
        prefer_lts: Prefer LTS versions over latest

    Returns:
        Dictionary with suggested versions and security info
    """
    vm = VersionManager()

    suggestions = {
        "recommended": vm.suggest_versions(tools, prefer_lts),
        "current": vm.get_versions(tools),
        "updates_available": vm.check_version_updates(tools),
    }

    if include_security:
        suggestions["security_updates"] = vm.get_security_updates(tools)

    return suggestions


def apply_version_updates(updates: Dict[str, str]) -> Dict[str, bool]:
    """Apply version updates and return success status for each tool."""
    vm = VersionManager()
    results = {}

    for tool, version in updates.items():
        results[tool] = vm.set_version(tool, version)

    vm.save_env_vars()
    return results
