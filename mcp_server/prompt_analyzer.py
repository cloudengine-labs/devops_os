"""Prompt analysis module for DevOps-OS MCP server.

Analyzes user prompts to detect gaps, missing details, and opportunities for
improvement. Provides heuristic-based detection of:
- Specificity levels
- Missing required parameters
- Vague language patterns
- Missing constraints and best practices
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptAnalysis:
    """Result of analyzing a user prompt."""
    
    tool_name: str
    prompt: str
    prompt_length: int
    has_specific_language: bool
    has_specific_cloud_provider: bool
    has_deployment_method: bool
    has_security_requirements: bool
    has_scalability_requirements: bool
    has_namespace_or_context: bool
    vague_words_found: list[str]
    tool_specific_gaps: dict[str, bool]
    overall_specificity_score: float  # 0.0 to 1.0


# Vague word patterns that suggest lack of specificity
VAGUE_WORDS = {
    "simple", "basic", "standard", "normal", "simple",
    "generic", "default", "minimal", "small", "easy",
    "quick", "fast", "just", "simply", "any"
}

# Programming languages
LANGUAGES = {
    "python", "java", "javascript", "typescript", "go", "rust",
    "csharp", "php", "kotlin", "c", "cpp", "ruby", "scala", "haskell"
}

# Cloud providers
CLOUD_PROVIDERS = {
    "aws", "gcp", "azure", "digitalocean", "linode", "heroku",
    "kubernetes", "k8s", "on-prem", "on-premise"
}

# Deployment/infrastructure methods
DEPLOYMENT_METHODS = {
    "docker", "kubernetes", "k8s", "helm", "kustomize", "argocd",
    "flux", "terraform", "cloudformation", "bicep", "pulumi",
    "kubectl", "iam", "ecs", "eks", "gke", "aks"
}

# Security/compliance keywords
SECURITY_KEYWORDS = {
    "security", "cis", "stig", "nsa", "compliance", "hardening",
    "policy", "kyverno", "inspec", "checkov", "pod security",
    "rbac", "network policy", "encrypt", "tls", "ssl"
}

# Scalability/HA keywords
SCALABILITY_KEYWORDS = {
    "scalable", "scaling", "ha", "high availability", "multi-region",
    "failover", "redundant", "replicas", "load balance", "auto-scale",
    "performance", "optimize", "latency", "throughput"
}

# Observability/monitoring keywords
OBSERVABILITY_KEYWORDS = {
    "monitoring", "observe", "metric", "alert", "log", "logging",
    "prometheus", "grafana", "slo", "sla", "apm", "observability",
    "tracing", "spans", "dashboard"
}


def _extract_words(text: str) -> set[str]:
    """Extract lowercase words from text."""
    return set(re.findall(r'\b\w+\b', text.lower()))


def _count_matches(text: str, keywords: set[str]) -> int:
    """Count how many keywords appear in text."""
    words = _extract_words(text)
    return len(words & keywords)


def _find_vague_words(prompt: str) -> list[str]:
    """Find vague words in the prompt."""
    words = _extract_words(prompt)
    return sorted(list(words & VAGUE_WORDS))


def analyze_prompt(tool_name: str, prompt: str) -> PromptAnalysis:
    """Analyze a user prompt for specificity and completeness.
    
    Args:
        tool_name: Name of the MCP tool being called (e.g., 'generate_github_actions_workflow')
        prompt: The user's prompt text
    
    Returns:
        PromptAnalysis object with detailed findings
    """
    prompt_lower = prompt.lower()
    words = _extract_words(prompt)
    prompt_length = len(prompt)
    
    # Check for specific languages
    has_specific_language = bool(words & LANGUAGES)
    
    # Check for cloud providers
    has_specific_cloud_provider = bool(words & CLOUD_PROVIDERS)
    
    # Check for deployment/infrastructure methods
    has_deployment_method = bool(words & DEPLOYMENT_METHODS)
    
    # Check for security requirements
    has_security_requirements = bool(words & SECURITY_KEYWORDS)
    
    # Check for scalability requirements
    has_scalability_requirements = bool(words & SCALABILITY_KEYWORDS)
    
    # Check for namespace/context specificity
    has_namespace_or_context = bool(
        re.search(r'\bnamespace\b', prompt_lower) or
        re.search(r'\benvironment\b', prompt_lower) or
        re.search(r'\bprod\w*\b', prompt_lower) or
        re.search(r'\bdev\w*\b', prompt_lower) or
        re.search(r'\bstag\w*\b', prompt_lower)
    )
    
    # Find vague words
    vague_words_found = _find_vague_words(prompt)
    
    # Tool-specific gap analysis
    tool_specific_gaps = _analyze_tool_specific_gaps(tool_name, prompt)
    
    # Calculate overall specificity score (0-1, higher is more specific)
    score = _calculate_specificity_score(
        prompt_length=prompt_length,
        has_language=has_specific_language,
        has_cloud=has_specific_cloud_provider,
        has_deployment=has_deployment_method,
        has_security=has_security_requirements,
        has_scalability=has_scalability_requirements,
        has_context=has_namespace_or_context,
        vague_word_count=len(vague_words_found),
        tool_gaps=tool_specific_gaps,
    )
    
    return PromptAnalysis(
        tool_name=tool_name,
        prompt=prompt,
        prompt_length=prompt_length,
        has_specific_language=has_specific_language,
        has_specific_cloud_provider=has_specific_cloud_provider,
        has_deployment_method=has_deployment_method,
        has_security_requirements=has_security_requirements,
        has_scalability_requirements=has_scalability_requirements,
        has_namespace_or_context=has_namespace_or_context,
        vague_words_found=vague_words_found,
        tool_specific_gaps=tool_specific_gaps,
        overall_specificity_score=score,
    )


def _analyze_tool_specific_gaps(tool_name: str, prompt: str) -> dict[str, bool]:
    """Analyze tool-specific gaps in the prompt.
    
    Args:
        tool_name: Name of the MCP tool
        prompt: The user's prompt text
    
    Returns:
        Dictionary with boolean flags for each gap type
    """
    gaps = {}
    words = _extract_words(prompt)
    
    if "github_actions" in tool_name or "gha" in tool_name:
        gaps["missing_language"] = len(words & LANGUAGES) == 0
        gaps["missing_cloud"] = len(words & CLOUD_PROVIDERS) == 0
        gaps["missing_deployment"] = len(words & DEPLOYMENT_METHODS) == 0
        gaps["missing_testing"] = "test" not in words and "unit" not in words
        
    elif "gitlab_ci" in tool_name or "gitlab" in tool_name:
        gaps["missing_language"] = len(words & LANGUAGES) == 0
        gaps["missing_deployment"] = len(words & DEPLOYMENT_METHODS) == 0
        gaps["missing_docker"] = "docker" not in words
        
    elif "jenkins" in tool_name:
        gaps["missing_language"] = len(words & LANGUAGES) == 0
        gaps["missing_pipeline_type"] = (
            "declarative" not in words and 
            "scripted" not in words and
            "pipeline" not in words
        )
        gaps["missing_scm"] = "git" not in words and "scm" not in words
        
    elif "k8s_config" in tool_name or "kubernetes" in tool_name:
        gaps["missing_namespace"] = (
            "namespace" not in words and
            not re.search(r'\bprod\w*\b', prompt.lower()) and
            not re.search(r'\bdev\w*\b', prompt.lower())
        )
        gaps["missing_replicas"] = "replicas" not in words and "replica" not in words
        gaps["missing_resources"] = "resource" not in words and "limit" not in words
        gaps["missing_labels"] = "label" not in words and "tag" not in words
        
    elif "argocd" in tool_name or "argoproj" in tool_name:
        gaps["missing_git_repo"] = "git" not in words and "repo" not in words
        gaps["missing_namespace"] = "namespace" not in words
        gaps["missing_sync_policy"] = "sync" not in words
        
    elif "sre_configs" in tool_name or "prometheus" in tool_name or "sre" in tool_name:
        gaps["missing_metrics"] = "metric" not in words
        gaps["missing_alert_threshold"] = "alert" not in words and "threshold" not in words
        gaps["missing_slo"] = "slo" not in words and "sla" not in words
        
    elif "devcontainer" in tool_name:
        gaps["missing_languages"] = len(words & LANGUAGES) == 0
        gaps["missing_tools"] = (
            "docker" not in words and
            "kubectl" not in words and
            "terraform" not in words
        )
    
    return gaps


def _calculate_specificity_score(
    prompt_length: int,
    has_language: bool,
    has_cloud: bool,
    has_deployment: bool,
    has_security: bool,
    has_scalability: bool,
    has_context: bool,
    vague_word_count: int,
    tool_gaps: dict[str, bool],
) -> float:
    """Calculate an overall specificity score (0.0 to 1.0).
    
    Args:
        prompt_length: Length of the prompt text
        has_language: Whether specific programming language mentioned
        has_cloud: Whether cloud provider mentioned
        has_deployment: Whether deployment method mentioned
        has_security: Whether security requirements mentioned
        has_scalability: Whether scalability requirements mentioned
        has_context: Whether context/namespace mentioned
        vague_word_count: Number of vague words found
        tool_gaps: Dictionary of tool-specific gaps
    
    Returns:
        Specificity score from 0.0 to 1.0
    """
    score = 0.0
    max_score = 10.0
    
    # Length contribution (up to 2 points)
    if prompt_length < 20:
        score += 0.5
    elif prompt_length < 50:
        score += 1.0
    elif prompt_length < 150:
        score += 1.5
    else:
        score += 2.0
    
    # Specific details (up to 6 points)
    if has_language:
        score += 1.0
    if has_cloud:
        score += 1.0
    if has_deployment:
        score += 1.0
    if has_security:
        score += 1.0
    if has_scalability:
        score += 1.0
    if has_context:
        score += 1.0
    
    # Vague words penalty (up to -2 points)
    score -= min(2.0, vague_word_count * 0.3)
    
    # Tool-specific gaps penalty (up to -2 points)
    gap_count = sum(1 for v in tool_gaps.values() if v)
    score -= min(2.0, gap_count * 0.25)
    
    # Normalize to 0-1 range
    final_score = max(0.0, min(1.0, score / max_score))
    return final_score
