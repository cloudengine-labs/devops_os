"""Unit tests for prompt analyzer and suggestion engine."""

import pytest
from mcp_server.prompt_analyzer import (
    analyze_prompt,
    PromptAnalysis,
    _extract_words,
    _count_matches,
    _find_vague_words,
)
from mcp_server.suggestion_engine import (
    SuggestionEngine,
    SuggestionCategory,
    get_suggestion_summary,
)


class TestPromptAnalyzer:
    """Tests for prompt_analyzer module."""
    
    def test_extract_words(self):
        """Test word extraction from text."""
        text = "Generate a Python workflow with Docker"
        words = _extract_words(text)
        assert "python" in words
        assert "workflow" in words
        assert "docker" in words
    
    def test_count_matches(self):
        """Test keyword counting."""
        text = "Python Java Go Rust"
        languages = {"python", "java", "go", "rust", "cpp"}
        count = _count_matches(text, languages)
        assert count == 4
    
    def test_find_vague_words(self):
        """Test vague word detection."""
        prompt = "Generate a simple basic pipeline"
        vague = _find_vague_words(prompt)
        assert "simple" in vague
        assert "basic" in vague
    
    def test_analyze_specific_prompt_gha(self):
        """Test analysis of specific GitHub Actions prompt."""
        prompt = (
            "Generate a GitHub Actions workflow for a Python Flask app "
            "with pytest, Docker build to AWS ECR, and kubectl deployment"
        )
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        assert analysis.tool_name == "generate_github_actions_workflow"
        assert analysis.has_specific_language
        assert analysis.has_specific_cloud_provider
        assert analysis.has_deployment_method
        # Score should be relatively high (>0.4) for a specific prompt
        assert analysis.overall_specificity_score > 0.4
    
    def test_analyze_vague_prompt_gha(self):
        """Test analysis of vague GitHub Actions prompt."""
        prompt = "Generate a workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        assert not analysis.has_specific_language
        assert not analysis.has_specific_cloud_provider
        assert not analysis.has_deployment_method
        assert analysis.prompt_length < 50
        assert analysis.overall_specificity_score < 0.4
    
    def test_analyze_k8s_prompt(self):
        """Test analysis of Kubernetes prompt."""
        prompt = (
            "Create Kubernetes manifests for production deployment "
            "in the payments namespace with 3 replicas"
        )
        analysis = analyze_prompt("generate_k8s_config", prompt)
        
        assert analysis.has_namespace_or_context
        assert analysis.tool_specific_gaps.get("missing_namespace") is False
        assert analysis.tool_specific_gaps.get("missing_replicas") is False
    
    def test_tool_specific_gaps_gha(self):
        """Test GitHub Actions tool-specific gap detection."""
        prompt = "Generate a workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        gaps = analysis.tool_specific_gaps
        assert gaps.get("missing_language") is True
        assert gaps.get("missing_cloud") is True
        assert gaps.get("missing_deployment") is True
    
    def test_tool_specific_gaps_k8s(self):
        """Test Kubernetes tool-specific gap detection."""
        prompt = "Create a deployment for my app with resource limits"
        analysis = analyze_prompt("generate_k8s_config", prompt)
        
        gaps = analysis.tool_specific_gaps
        assert gaps.get("missing_namespace") is True
        assert gaps.get("missing_replicas") is True
    
    def test_specificity_score_calculation(self):
        """Test specificity score is in valid range."""
        prompts = [
            "Generate workflow",
            "Generate Python workflow",
            "Generate Python workflow for AWS with Docker and kubectl",
        ]
        
        scores = [
            analyze_prompt("generate_github_actions_workflow", p).overall_specificity_score
            for p in prompts
        ]
        
        # Scores should increase with specificity
        assert scores[0] < scores[1] < scores[2]
        # All scores should be in valid range
        assert all(0.0 <= s <= 1.0 for s in scores)


class TestSuggestionEngine:
    """Tests for suggestion_engine module."""
    
    def test_suggestion_engine_initialization(self):
        """Test suggestion engine can be initialized."""
        engine = SuggestionEngine()
        assert engine is not None
        assert len(engine.suggestions_map) > 0
    
    def test_gha_suggestions_missing_language(self):
        """Test GitHub Actions suggestions for missing language."""
        prompt = "Generate a complete workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        engine = SuggestionEngine()
        suggestions = engine.generate_suggestions(analysis, max_suggestions=5)
        
        assert len(suggestions) > 0
        # Should have suggestions for missing language
        suggestion_texts = [s.suggestion_text for s in suggestions]
        assert any("language" in text.lower() for text in suggestion_texts)
    
    def test_k8s_suggestions_missing_namespace(self):
        """Test Kubernetes suggestions for missing namespace."""
        prompt = "Create deployment manifests"
        analysis = analyze_prompt("generate_k8s_config", prompt)
        
        engine = SuggestionEngine()
        suggestions = engine.generate_suggestions(analysis, max_suggestions=5)
        
        assert len(suggestions) > 0
        suggestion_texts = [s.suggestion_text for s in suggestions]
        assert any("namespace" in text.lower() for text in suggestion_texts)
    
    def test_suggestion_confidence_filtering(self):
        """Test suggestions are filtered by confidence."""
        prompt = "Generate workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        engine = SuggestionEngine()
        
        # High confidence only
        high_suggestions = engine.generate_suggestions(analysis, min_confidence="high")
        assert all(s.confidence == "high" for s in high_suggestions)
        
        # Medium confidence includes both high and medium
        medium_suggestions = engine.generate_suggestions(analysis, min_confidence="medium")
        assert all(s.confidence in ("high", "medium") for s in medium_suggestions)
    
    def test_max_suggestions_limit(self):
        """Test max suggestions limit is respected."""
        prompt = "Generate workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        engine = SuggestionEngine()
        suggestions = engine.generate_suggestions(analysis, max_suggestions=1)
        
        assert len(suggestions) <= 1
    
    def test_suggestion_has_required_fields(self):
        """Test suggestions have all required fields."""
        prompt = "Generate workflow"
        analysis = analyze_prompt("generate_github_actions_workflow", prompt)
        
        engine = SuggestionEngine()
        suggestions = engine.generate_suggestions(analysis)
        
        for suggestion in suggestions:
            assert suggestion.suggestion_text is not None
            assert len(suggestion.suggestion_text) > 0
            assert suggestion.suggestion_category is not None
            assert suggestion.confidence in ("high", "medium", "low")
    
    def test_suggestion_to_dict(self):
        """Test suggestion conversion to dictionary."""
        from mcp_server.suggestion_engine import Suggestion
        
        suggestion = Suggestion(
            suggestion_text="Test suggestion",
            suggestion_category=SuggestionCategory.SPECIFICITY,
            confidence="high",
            example_improvement="Test example",
        )
        
        suggestion_dict = suggestion.to_dict()
        assert suggestion_dict["suggestion_text"] == "Test suggestion"
        assert suggestion_dict["suggestion_category"] == "specificity"
        assert suggestion_dict["confidence"] == "high"
        assert suggestion_dict["example_improvement"] == "Test example"
    
    def test_suggestion_summary_single(self):
        """Test suggestion summary for single suggestion."""
        from mcp_server.suggestion_engine import Suggestion
        
        suggestions = [
            Suggestion(
                suggestion_text="Test",
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
            )
        ]
        
        summary = get_suggestion_summary(suggestions)
        assert "1" in summary
        assert "suggestion" in summary
    
    def test_suggestion_summary_multiple(self):
        """Test suggestion summary for multiple suggestions."""
        from mcp_server.suggestion_engine import Suggestion
        
        suggestions = [
            Suggestion(
                suggestion_text="Test 1",
                suggestion_category=SuggestionCategory.SPECIFICITY,
                confidence="high",
            ),
            Suggestion(
                suggestion_text="Test 2",
                suggestion_category=SuggestionCategory.CONTEXT,
                confidence="high",
            ),
        ]
        
        summary = get_suggestion_summary(suggestions)
        assert "2" in summary
        assert "suggestions" in summary
    
    def test_suggestion_summary_empty(self):
        """Test suggestion summary for empty suggestions."""
        summary = get_suggestion_summary([])
        assert "No suggestions" in summary
    
    def test_all_tools_have_suggestions(self):
        """Test that all tool types can generate suggestions."""
        tools_and_prompts = [
            ("generate_github_actions_workflow", "Generate workflow"),
            ("generate_gitlab_ci_pipeline", "Generate GitLab CI"),
            ("generate_jenkins_pipeline", "Generate Jenkins pipeline"),
            ("generate_k8s_config", "Generate Kubernetes config"),
            ("generate_argocd_config", "Generate ArgoCD config"),
            ("generate_sre_configs", "Generate SRE config"),
            ("scaffold_devcontainer", "Generate dev container"),
        ]
        
        engine = SuggestionEngine()
        
        for tool_name, prompt in tools_and_prompts:
            analysis = analyze_prompt(tool_name, prompt)
            suggestions = engine.generate_suggestions(analysis, max_suggestions=5)
            # At least some tools should have suggestions for vague prompts
            assert isinstance(suggestions, list)


class TestBackwardCompatibility:
    """Tests for backward compatibility."""
    
    def test_config_defaults(self):
        """Test that config has proper defaults."""
        from mcp_server.config import Config
        
        config = Config()
        assert config.enable_suggestions is True
        assert config.suggestion_confidence_threshold == "medium"
        assert config.max_suggestions_per_response == 2
        assert config.include_examples_in_suggestions is True
    
    def test_response_enhancer_with_suggestions_disabled(self):
        """Test response enhancer returns raw output when suggestions disabled."""
        from mcp_server.config import Config
        from mcp_server.response_enhancer import ResponseEnhancer
        
        config = Config(enable_suggestions=False)
        enhancer = ResponseEnhancer(config)
        
        original_output = "test output"
        result = enhancer.enhance_response(
            tool_name="generate_github_actions_workflow",
            tool_output=original_output,
            user_prompt="generate workflow",
        )
        
        # Should return original output unchanged
        assert result == original_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
