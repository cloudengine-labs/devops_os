#!/usr/bin/env python3
"""
DevOps-OS Version Management Examples

Demonstrates how to use the version management MCP tools and version_manager
module for managing development environment tool versions with security awareness.

Run this script to see practical examples of:
- Checking current version configuration
- Finding available updates
- Getting version suggestions
- Updating versions
- Detecting security issues
"""

import json
from mcp_server.version_manager import VersionManager, get_version_suggestions
from mcp_server.devcontainer_mcp import (
    get_version_config,
    get_version_updates,
    suggest_versions,
    check_security_issues,
    update_versions,
)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def example_1_audit_versions():
    """Example 1: Audit current version configuration."""
    print_section("Example 1: Audit Current Versions")
    
    result = get_version_config("python,go,node,java,docker")
    result_dict = json.loads(result) if isinstance(result, str) else result
    
    print("Current configuration:")
    for tool, version in result_dict.get("current_versions", {}).items():
        info = result_dict.get("tools_info", {}).get(tool, {})
        status = info.get("status", "unknown")
        print(f"  • {tool:12} → {version:10} [{status}]")


def example_2_check_updates():
    """Example 2: Check for available updates."""
    print_section("Example 2: Check for Available Updates")
    
    result = get_version_updates("python,java,node")
    result_dict = json.loads(result) if isinstance(result, str) else result
    
    summary = result_dict.get("summary", {})
    print(f"Summary:")
    print(f"  • Tools checked: {summary.get('tools_checked')}")
    print(f"  • Updates available: {summary.get('updates_available')}")
    print(f"  • Security issues: {summary.get('security_issues')}")
    
    print("\nDetailed updates:")
    for tool, update in result_dict.get("available_updates", {}).items():
        can_update = update.get("can_update")
        security = update.get("security_level")
        status = "⚠️ YES" if can_update else "✓ NO"
        print(f"  • {tool}: current={update.get('current')}, "
              f"latest={update.get('latest')}, can_update={status} "
              f"[{security} security]")


def example_3_lts_vs_latest():
    """Example 3: Compare LTS vs Latest suggestions."""
    print_section("Example 3: LTS vs Latest Versions Strategy")
    
    tools = "python,java,go,node,ruby"
    
    # Get LTS suggestions
    lts_result = suggest_versions(tools, prefer_lts=True)
    lts_dict = json.loads(lts_result) if isinstance(lts_result, str) else lts_result
    lts_suggestions = lts_dict.get("suggested_versions", {})
    current = lts_dict.get("current_versions", {})
    
    # Get Latest suggestions
    latest_result = suggest_versions(tools, prefer_lts=False)
    latest_dict = json.loads(latest_result) if isinstance(latest_result, str) else latest_result
    latest_suggestions = latest_dict.get("suggested_versions", {})
    
    print("Version comparison (Current → LTS → Latest):")
    for tool in sorted(current.keys()):
        curr = current.get(tool)
        lts = lts_suggestions.get(tool)
        latest = latest_suggestions.get(tool)
        lts_indicator = "→" if lts != curr else " "
        latest_indicator = "→" if latest != curr else " "
        print(f"  • {tool:8} {curr:8} {lts_indicator} {lts:8} {latest_indicator} {latest}")


def example_4_security_audit():
    """Example 4: Security audit - find vulnerable versions."""
    print_section("Example 4: Security Issues Detection")
    
    # Simulate having older versions by directly updating
    vm = VersionManager()
    vm.versions["python"] = "3.8"  # EOL, critical security
    
    result = check_security_issues("python,java")
    result_dict = json.loads(result) if isinstance(result, str) else result
    
    assessment = result_dict.get("security_assessment", {})
    
    # Print by urgency
    for urgency in ["critical", "high", "medium", "low"]:
        issues = assessment.get(urgency, {})
        if issues:
            print(f"{urgency.upper()} Urgency ({len(issues)} issue{'s' if len(issues) != 1 else ''}):")
            for tool, info in issues.items():
                print(f"  ⚠️  {tool}: {info.get('current')} → "
                      f"{info.get('recommended')} "
                      f"({info.get('reason')})")


def example_5_update_workflow():
    """Example 5: Complete update workflow."""
    print_section("Example 5: Complete Update Workflow")
    
    # Step 1: Current state
    print("Step 1: Check current versions")
    result = get_version_config("python,go,node")
    result_dict = json.loads(result) if isinstance(result, str) else result
    current = result_dict.get("current_versions", {})
    print(f"  Current: {current}")
    
    # Step 2: Get recommendations
    print("\nStep 2: Get LTS recommendations")
    result = suggest_versions("python,go,node", prefer_lts=True)
    result_dict = json.loads(result) if isinstance(result, str) else result
    recommendations = result_dict.get("suggested_versions", {})
    print(f"  Recommended: {recommendations}")
    
    # Step 3: Update
    print("\nStep 3: Apply updates")
    updates_json = json.dumps(recommendations)
    result = update_versions(updates_json)
    result_dict = json.loads(result) if isinstance(result, str) else result
    
    if result_dict.get("success"):
        print("  ✓ Updates applied successfully")
        new_versions = result_dict.get("new_versions", {})
        for tool, version in new_versions.items():
            print(f"    • {tool}: {version}")
    else:
        print(f"  ✗ Update failed: {result_dict.get('error')}")


def example_6_env_file_management():
    """Example 6: Working with .env files."""
    print_section("Example 6: Environment File Management")
    
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, ".env")
        
        # Create version manager and save to file
        vm = VersionManager()
        versions = {
            "python": "3.12",
            "java": "21",
            "go": "1.25.0",
            "node": "22",
            "docker": "27.0.0",
            "kubectl": "1.31.0",
            "terraform": "1.9.0",
        }
        
        vm.save_env_file(env_file, versions)
        print(f"✓ Saved versions to {env_file}")
        
        # Show file content
        print("\nFile content:")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"  {line}")


def example_7_version_database():
    """Example 7: Explore version database."""
    print_section("Example 7: Version Database Information")
    
    from mcp_server.version_manager import VERSION_DATABASE
    
    print("Available tools in database:")
    tools = sorted(VERSION_DATABASE.keys())
    
    for i, tool in enumerate(tools, 1):
        db = VERSION_DATABASE[tool]
        default = db.get("default")
        latest = db.get("latest")
        lts_versions = ", ".join(db.get("lts", [])[:2])
        
        print(f"  {i:2}. {tool:15} default={default:10} latest={latest:10} lts=[{lts_versions}]")


def example_8_mcp_tool_reference():
    """Example 8: MCP Tool Reference Guide."""
    print_section("Example 8: MCP Tools Reference")
    
    tools = [
        {
            "name": "get_version_config",
            "description": "Get current version configuration",
            "params": "tools (optional, comma-separated)",
            "use_case": "Audit current environment versions",
        },
        {
            "name": "check_version_updates",
            "description": "Check for available updates",
            "params": "tools (optional, comma-separated)",
            "use_case": "Find tools that have new versions available",
        },
        {
            "name": "suggest_versions",
            "description": "Get version recommendations",
            "params": "tools (optional), prefer_lts (boolean)",
            "use_case": "Plan version upgrades (LTS or latest)",
        },
        {
            "name": "update_versions",
            "description": "Update tool versions",
            "params": "versions_json (JSON dict)",
            "use_case": "Apply version changes to environment",
        },
        {
            "name": "check_security_issues",
            "description": "Detect security vulnerabilities",
            "params": "tools (optional, comma-separated)",
            "use_case": "Find versions with security issues",
        },
    ]
    
    print("Available MCP Tools:\n")
    for tool in tools:
        print(f"  📌 {tool['name']}")
        print(f"     Description: {tool['description']}")
        print(f"     Parameters:  {tool['params']}")
        print(f"     Use case:    {tool['use_case']}")
        print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  DevOps-OS Version Management Examples")
    print("=" * 70)
    
    try:
        example_1_audit_versions()
        example_2_check_updates()
        example_3_lts_vs_latest()
        example_4_security_audit()
        example_5_update_workflow()
        example_6_env_file_management()
        example_7_version_database()
        example_8_mcp_tool_reference()
        
        print_section("Examples Complete!")
        print("✓ All examples ran successfully")
        print("\nNext steps:")
        print("  1. Review the version management documentation: version-management.md")
        print("  2. Try the MCP tools in your environment")
        print("  3. Set up .env file for team consistency")
        print("  4. Use check_security_issues() regularly to stay secure")
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
