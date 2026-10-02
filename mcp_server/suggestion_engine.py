"""Suggestion engine for prompt improvements.

Generates contextual suggestions based on prompt analysis. Provides
human-readable recommendations to help users improve their prompts
and get better DevOps configurations.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from mcp_server.prompt_analyzer import PromptAnalysis


class SuggestionCategory(str, Enum):
    """Categories of suggestions."""
    SPECIFICITY = "specificity"
    CONTEXT = "context"
    BEST_PRACTICE = "best_practice"
    COMPLETENESS = "completeness"
    OPTIMIZATION = "optimization"


@dataclass
class Suggestion:
    """A single suggestion for prompt improvement."""
    
    suggestion_text: str
    suggestion_category: SuggestionCategory
    confidence: str  # "high", "medium", "low"
    example_improvement: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "suggestion_text": self.suggestion_text,
            "suggestion_category": self.suggestion_category.value,
            "confidence": self.confidence,
            "example_improvement": self.example_improvement,
        }


class SuggestionEngine:
    """Generates improvement suggestions based on prompt analysis."""
    
    def __init__(self):
        """Initialize the suggestion engine."""
        self.suggestions_map = self._build_suggestions_map()
    
    def _build_suggestions_map(self) -> dict:
        """Build a map of tool names to suggestion templates."""
        return {
            "generate_github_actions_workflow": self._suggestions_for_gha,
            "generate_gitlab_ci_pipeline": self._suggestions_for_gitlab,
            "generate_jenkins_pipeline": self._suggestions_for_jenkins,
            "generate_k8s_config": self._suggestions_for_k8s,
            "generate_argocd_config": self._suggestions_for_argocd,
            "generate_sre_configs": self._suggestions_for_sre,
            "scaffold_devcontainer": self._suggestions_for_devcontainer,
        }
    
    def generate_suggestions(
        self,
        analysis: PromptAnalysis,
        max_suggestions: int = 2,
        min_confidence: str = "medium",
    ) -> list[Suggestion]:
        """Generate suggestions based on prompt analysis.
        
        Args:
            analysis: PromptAnalysis object from prompt_analyzer
            max_suggestions: Maximum number of suggestions to return
            min_confidence: Minimum confidence level ("high", "medium", "low")
        
        Returns:
            List of Suggestion objects, ordered by importance
        """
        # Get tool-specific suggestions
        suggestion_func = self.suggestions_map.get(
            analysis.tool_name,
            self._suggestions_generic,
        )
        
        all_suggestions = suggestion_func(analysis)
        
        # Filter by confidence
        confidence_order = {"high": 0, "medium": 1, "low": 2}
        min_confidence_level = confidence_order.get(min_confidence, 1)
        
        filtered = [
            s for s in all_suggestions
            if confidence_order[s.confidence] <= min_confidence_level
        ]
        
        # Sort by confidence (high first) then by our internal ordering
        sorted_suggestions = sorted(
            filtered,
            key=lambda s: (confidence_order[s.confidence], all_suggestions.index(s)),
        )
        
        return sorted_suggestions[:max_suggestions]
    
    def _suggestions_for_gha(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for GitHub Actions workflows."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_language"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Consider specifying a programming language (Python, Node.js, Go, Java, etc.) "
                    "for more optimized and language-specific workflow steps"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
                example_improvement=(
                    "Generate a GitHub Actions workflow for a Python project with pytest, "
                    "Docker build, and deployment to AWS"
                ),
            ))
        
        if gaps.get("missing_cloud"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify your deployment cloud provider (AWS, GCP, Azure) to optimize "
                    "deployment credentials and infrastructure automation"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
                example_improvement="...deploy to AWS using ECR and ECS credentials...",
            ))
        
        if gaps.get("missing_deployment"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention your deployment method (Docker push, Kubernetes kubectl, "
                    "Helm, ArgoCD) for deployment-specific workflow steps"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="high",
                example_improvement="...build Docker image and deploy via kubectl...",
            ))
        
        if gaps.get("missing_testing"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Include testing framework details (pytest, Jest, JUnit, etc.) "
                    "to enable comprehensive test automation in your workflow"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="medium",
                example_improvement="...include pytest for Python unit tests and coverage...",
            ))
        
        if not analysis.has_security_requirements:
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Consider adding security scanning steps (SAST, dependency check, "
                    "vulnerability scanning) for production-ready workflows"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="medium",
            ))
        
        if analysis.prompt_length < 50:
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Provide more details about your build and deployment requirements. "
                    "More specific prompts lead to better configurations."
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="low",
            ))
        
        return suggestions
    
    def _suggestions_for_gitlab(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for GitLab CI pipelines."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_language"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify your programming language for appropriate build image "
                    "and pipeline configuration"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
                example_improvement=(
                    "Generate a GitLab CI pipeline for a Python Flask application "
                    "with Docker build and Kubernetes deployment"
                ),
            ))
        
        if gaps.get("missing_docker"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention whether you need Docker image building and registry "
                    "configuration (GitLab Container Registry, Docker Hub, etc.)"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
            ))
        
        if gaps.get("missing_deployment"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify deployment target and method (Kubernetes, Helm, "
                    "cloud platform) for automated deployment stages"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="high",
            ))
        
        return suggestions
    
    def _suggestions_for_jenkins(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for Jenkins pipelines."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_language"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify your programming language to enable language-specific "
                    "build tools and testing frameworks"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
                example_improvement=(
                    "Generate a Jenkins declarative pipeline for a Java Maven project "
                    "with SonarQube analysis and artifact deployment"
                ),
            ))
        
        if gaps.get("missing_pipeline_type"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention pipeline type (declarative vs scripted) and key stages "
                    "(build, test, deploy) you need"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="high",
            ))
        
        if gaps.get("missing_scm"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify your source control system (Git, GitHub, GitLab) "
                    "for proper SCM configuration"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="medium",
            ))
        
        return suggestions
    
    def _suggestions_for_k8s(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for Kubernetes configs."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_namespace"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify a namespace (e.g., production, staging, development) "
                    "for proper resource isolation and organization"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
                example_improvement=(
                    "Generate Kubernetes manifests for a production deployment "
                    "in the payments namespace with resource limits"
                ),
            ))
        
        if gaps.get("missing_replicas"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify the number of replicas for high availability and load balancing"
                ),
                suggestion_category=SuggestionCategory.OPTIMIZATION,
                confidence="high",
                example_improvement="...with 3 replicas for high availability...",
            ))
        
        if gaps.get("missing_resources"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Include resource requests and limits (CPU, memory) "
                    "for proper scheduling and resource management"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="high",
                example_improvement="...with CPU limit of 500m and memory limit of 512Mi...",
            ))
        
        if gaps.get("missing_labels"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention labels for service discovery, monitoring, and resource selection"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="medium",
            ))
        
        if not analysis.has_security_requirements:
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Consider specifying security requirements (network policies, "
                    "RBAC, pod security standards) for production deployments"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="medium",
            ))
        
        return suggestions
    
    def _suggestions_for_argocd(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for ArgoCD configs."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_git_repo"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify your Git repository URL for ArgoCD to sync configurations"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
                example_improvement=(
                    "Generate ArgoCD Application config syncing from "
                    "https://github.com/yourorg/configs repository"
                ),
            ))
        
        if gaps.get("missing_namespace"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify target namespace (production, staging, etc.) "
                    "for deployment"
                ),
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
            ))
        
        if gaps.get("missing_sync_policy"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention sync strategy (automatic, manual) and pruning preferences "
                    "for deployment automation"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="medium",
            ))
        
        return suggestions
    
    def _suggestions_for_sre(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for SRE configs (Prometheus, Grafana)."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_metrics"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify key metrics to monitor (latency, error rate, throughput, "
                    "CPU, memory, etc.)"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
                example_improvement=(
                    "Generate Prometheus alert rules for a payment service monitoring "
                    "p99 latency > 500ms, error rate > 1%, and CPU > 80%"
                ),
            ))
        
        if gaps.get("missing_alert_threshold"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Include alert thresholds and conditions (e.g., latency > 500ms, "
                    "error rate > 1%) for proper alerting"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="high",
            ))
        
        if gaps.get("missing_slo"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Mention SLO/SLA targets (e.g., 99.9% availability, 500ms response time) "
                    "for SLO-based monitoring"
                ),
                suggestion_category=SuggestionCategory.BEST_PRACTICE,
                confidence="medium",
            ))
        
        return suggestions
    
    def _suggestions_for_devcontainer(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate suggestions for dev container configs."""
        suggestions = []
        gaps = analysis.tool_specific_gaps
        
        if gaps.get("missing_languages"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Specify programming languages you need (Python, Node.js, Go, Java, etc.) "
                    "for proper language tools and runtime installation"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
                example_improvement=(
                    "Generate a dev container with Python 3.11, Node.js 20, "
                    "Docker, Kubernetes CLI, and Terraform"
                ),
            ))
        
        if gaps.get("missing_tools"):
            suggestions.append(Suggestion(
                suggestion_text=(
                    "List the development tools you need (Docker, Kubernetes, Terraform, "
                    "Helm, etc.) for automated setup"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="high",
            ))
        
        return suggestions
    
    def _suggestions_generic(self, analysis: PromptAnalysis) -> list[Suggestion]:
        """Generate generic suggestions for any tool."""
        suggestions = []
        
        if analysis.prompt_length < 30:
            suggestions.append(Suggestion(
                suggestion_text=(
                    "Your prompt is quite brief. Providing more details about your "
                    "requirements, infrastructure, and constraints will result in better configurations"
                ),
                suggestion_category=SuggestionCategory.COMPLETENESS,
                confidence="medium",
            ))
        
        if analysis.vague_words_found:
            vague_list = ", ".join(f'"{w}"' for w in analysis.vague_words_found[:3])
            suggestions.append(Suggestion(
                suggestion_text=(
                    f"Avoid vague terms like {vague_list}. Be specific about your exact requirements "
                    "and infrastructure needs for better results"
                ),
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="medium",
            ))
        
        return suggestions


def get_suggestion_summary(suggestions: list[Suggestion]) -> str:
    """Generate a human-readable summary of suggestions.
    
    Args:
        suggestions: List of Suggestion objects
    
    Returns:
        Summary string (e.g., "2 suggestions to improve future prompts")
    """
    if not suggestions:
        return "No suggestions needed - great prompt!"
    
    count = len(suggestions)
    high_count = sum(1 for s in suggestions if s.confidence == "high")
    
    if high_count == count:
        return f"{count} important suggestion{'s' if count > 1 else ''} to improve results"
    else:
        return f"{count} suggestion{'s' if count > 1 else ''} to improve future prompts"
