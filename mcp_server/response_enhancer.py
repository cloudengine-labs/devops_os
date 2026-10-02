"""Response enhancement module for adding prompt suggestions to tool outputs.

This module provides utilities to wrap tool results with prompt improvement
suggestions, maintaining backward compatibility while enriching the response.
"""

import json
from typing import Any, Optional
from dataclasses import asdict

from mcp_server.prompt_analyzer import analyze_prompt
from mcp_server.suggestion_engine import SuggestionEngine, get_suggestion_summary
from mcp_server.config import Config


class ResponseEnhancer:
    """Enhances tool responses with prompt improvement suggestions."""
    
    def __init__(self, config: Config):
        """Initialize the response enhancer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.suggestion_engine = SuggestionEngine()
    
    def enhance_response(
        self,
        tool_name: str,
        tool_output: str,
        user_prompt: str,
    ) -> str:
        """Enhance a tool response with prompt suggestions.
        
        If suggestions are disabled, returns the original tool output unchanged.
        If enabled, wraps the output with suggestions in a structured format.
        
        Args:
            tool_name: Name of the tool that was called
            tool_output: The tool's original output
            user_prompt: The user's original prompt/input
        
        Returns:
            Enhanced response with suggestions (or original output if disabled)
        """
        # If suggestions are disabled, return the original output
        if not self.config.enable_suggestions:
            return tool_output
        
        # Analyze the prompt
        analysis = analyze_prompt(tool_name, user_prompt)
        
        # Generate suggestions
        suggestions = self.suggestion_engine.generate_suggestions(
            analysis,
            max_suggestions=self.config.max_suggestions_per_response,
            min_confidence=self.config.suggestion_confidence_threshold,
        )
        
        # If no suggestions, return original output
        if not suggestions:
            return tool_output
        
        # Build the enhanced response structure
        response_dict = {
            "tool_output": tool_output,
            "prompt_analysis": {
                "specificity_score": round(analysis.overall_specificity_score, 2),
                "prompt_length": analysis.prompt_length,
                "has_language_specified": analysis.has_specific_language,
                "has_cloud_provider_specified": analysis.has_specific_cloud_provider,
                "has_deployment_method_specified": analysis.has_deployment_method,
            },
            "prompt_suggestions": [
                s.to_dict() for s in suggestions
            ],
            "suggestion_summary": get_suggestion_summary(suggestions),
        }
        
        # Filter out example improvements if configured
        if not self.config.include_examples_in_suggestions:
            for suggestion in response_dict["prompt_suggestions"]:
                suggestion.pop("example_improvement", None)
        
        # Return as JSON string
        return json.dumps(response_dict, indent=2)
    
    def should_include_suggestions_for_prompt(self, user_prompt: str) -> bool:
        """Determine if suggestions should be generated for this prompt.
        
        Args:
            user_prompt: The user's prompt text
        
        Returns:
            True if suggestions should be generated
        """
        if not self.config.enable_suggestions:
            return False
        
        # Always include suggestions if enabled
        return True
    
    def get_suggestion_context_for_tool(
        self,
        tool_name: str,
        user_prompt: str,
    ) -> Optional[dict]:
        """Get suggestion context for a specific tool and prompt.
        
        Useful for logging and analytics.
        
        Args:
            tool_name: Name of the tool
            user_prompt: User's prompt
        
        Returns:
            Dictionary with analysis context or None if suggestions disabled
        """
        if not self.config.enable_suggestions:
            return None
        
        analysis = analyze_prompt(tool_name, user_prompt)
        suggestions = self.suggestion_engine.generate_suggestions(
            analysis,
            max_suggestions=self.config.max_suggestions_per_response,
            min_confidence=self.config.suggestion_confidence_threshold,
        )
        
        return {
            "tool_name": tool_name,
            "suggestion_count": len(suggestions),
            "specificity_score": analysis.overall_specificity_score,
            "prompt_length": analysis.prompt_length,
            "suggestion_categories": [s.suggestion_category.value for s in suggestions],
        }
