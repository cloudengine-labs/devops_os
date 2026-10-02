"""Input validation for DevOps-OS MCP tools.

Validates tool inputs to prevent invalid configurations and potential security issues.
"""

import re
from typing import Any


class ValidationError(ValueError):
    """Raised when tool input validation fails."""

    pass


def validate_k8s_identifier(value: str, field_name: str, allow_dots: bool = False) -> str:
    """Validate a Kubernetes identifier (app name, service name, etc.).

    Valid: 1-63 lowercase alphanumeric characters and dashes, starting and ending with alphanumeric.
    Examples: my-app, api-service-v1, backend

    Args:
        value: The identifier to validate
        field_name: Name of the field (for error messages)
        allow_dots: If True, allow dots in identifier (for domain names)

    Returns:
        The validated identifier

    Raises:
        ValidationError: If identifier is invalid
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    if len(value) > 63:
        raise ValidationError(
            f"{field_name} must be 1-63 characters, got {len(value)}"
        )

    # Kubernetes DNS subdomain names must consist of lowercase alphanumeric characters, '-',
    # and start and end with an alphanumeric character
    if allow_dots:
        pattern = r"^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$"
    else:
        pattern = r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"

    if not re.match(pattern, value):
        raise ValidationError(
            f"{field_name} must contain only lowercase alphanumeric characters and dashes, "
            f"starting and ending with alphanumeric. Got: {value}"
        )

    return value


def validate_image_reference(value: str) -> str:
    """Validate a Docker image reference.

    Ensures the reference is properly formatted (no shell injection, etc).
    Examples: ghcr.io/myorg/myapp:v1.0.0, python:3.12, alpine

    Args:
        value: The image reference to validate

    Returns:
        The validated reference

    Raises:
        ValidationError: If reference is invalid
    """
    if not value:
        raise ValidationError("Image reference cannot be empty")

    if len(value) > 256:
        raise ValidationError(
            f"Image reference must be 1-256 characters, got {len(value)}"
        )

    # Reject common shell injection patterns
    dangerous_chars = [";", "|", "&", "`", "$", "(", ")", "<", ">", "\n", "\r"]
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(
                f"Image reference contains invalid character: {repr(char)}"
            )

    # Basic docker reference format validation
    # Format: [registry/]name[:tag][@digest]
    # See: https://github.com/docker/distribution/blob/main/reference/reference.go
    if value.count(":") > 1 and value.count("@") == 0:
        raise ValidationError(f"Invalid image reference format: {value}")

    return value


def validate_port(value: int | str, field_name: str = "port") -> int:
    """Validate a network port number.

    Args:
        value: The port to validate (int or str)
        field_name: Name of the field (for error messages)

    Returns:
        The validated port as int

    Raises:
        ValidationError: If port is invalid
    """
    try:
        port_int = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be an integer, got {value}")

    if not 1 <= port_int <= 65535:
        raise ValidationError(f"{field_name} must be 1-65535, got {port_int}")

    return port_int


def validate_positive_int(value: int | str, field_name: str, max_val: int | None = None) -> int:
    """Validate a positive integer.

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        max_val: Maximum allowed value (optional)

    Returns:
        The validated value as int

    Raises:
        ValidationError: If value is invalid
    """
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be an integer, got {value}")

    if int_val <= 0:
        raise ValidationError(f"{field_name} must be positive, got {int_val}")

    if max_val is not None and int_val > max_val:
        raise ValidationError(
            f"{field_name} must be <= {max_val}, got {int_val}"
        )

    return int_val


def validate_replica_count(value: int | str) -> int:
    """Validate a Kubernetes replica count.

    Args:
        value: The replica count to validate

    Returns:
        The validated count

    Raises:
        ValidationError: If count is invalid
    """
    return validate_positive_int(value, "replicas", max_val=100)


def validate_choice(value: str, choices: list[str], field_name: str) -> str:
    """Validate that a value is in a list of allowed choices.

    Args:
        value: The value to validate
        choices: List of allowed values
        field_name: Name of the field (for error messages)

    Returns:
        The validated value

    Raises:
        ValidationError: If value is not in choices
    """
    if value not in choices:
        raise ValidationError(
            f"{field_name} must be one of {choices}, got {repr(value)}"
        )
    return value


def validate_float_range(
    value: float | str, field_name: str, min_val: float = 0.0, max_val: float = 100.0
) -> float:
    """Validate a float within a range.

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        The validated value as float

    Raises:
        ValidationError: If value is invalid
    """
    try:
        float_val = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number, got {value}")

    if not min_val <= float_val <= max_val:
        raise ValidationError(
            f"{field_name} must be {min_val}-{max_val}, got {float_val}"
        )

    return float_val


def validate_slo_target(value: float | str) -> float:
    """Validate a Service Level Objective target percentage.

    Args:
        value: The SLO target (e.g., 99.9 for 99.9%)

    Returns:
        The validated target

    Raises:
        ValidationError: If target is invalid
    """
    return validate_float_range(value, "SLO target", min_val=50.0, max_val=99.99)


def validate_string_length(value: str, field_name: str, max_len: int = 256) -> str:
    """Validate a string length.

    Args:
        value: The string to validate
        field_name: Name of the field (for error messages)
        max_len: Maximum allowed length

    Returns:
        The validated string

    Raises:
        ValidationError: If string is too long
    """
    if len(value) > max_len:
        raise ValidationError(
            f"{field_name} must be 1-{max_len} characters, got {len(value)}"
        )
    return value


def validate_languages(value: str) -> str:
    """Validate a comma-separated list of languages.

    Args:
        value: Comma-separated language list (e.g., 'python,javascript,go')

    Returns:
        The validated value

    Raises:
        ValidationError: If value is invalid
    """
    if not value:
        raise ValidationError("languages cannot be empty")

    valid_languages = {
        "python", "javascript", "typescript", "go", "java", "rust", "csharp",
        "php", "ruby", "kotlin", "swift", "c", "cpp", "r"
    }

    languages = [lang.strip().lower() for lang in value.split(",")]
    invalid = [lang for lang in languages if lang and lang not in valid_languages]

    if invalid:
        raise ValidationError(
            f"Invalid languages: {invalid}. Supported: {sorted(valid_languages)}"
        )

    return value


def validate_tool_inputs(tool_name: str, **kwargs) -> dict[str, Any]:
    """Validate tool-specific inputs.

    This is the main entry point for tool validation.

    Args:
        tool_name: Name of the tool
        **kwargs: Tool-specific arguments

    Returns:
        Validated arguments dict

    Raises:
        ValidationError: If any input is invalid
    """
    validated = kwargs.copy()

    # Tool: generate_github_actions_workflow
    if tool_name == "generate_github_actions_workflow":
        if "name" in validated:
            validated["name"] = validate_k8s_identifier(validated["name"], "name")
        if "languages" in validated:
            validated["languages"] = validate_languages(validated["languages"])
        if "workflow_type" in validated:
            validated["workflow_type"] = validate_choice(
                validated["workflow_type"],
                ["build", "test", "deploy", "complete", "reusable"],
                "workflow_type",
            )

    # Tool: generate_jenkins_pipeline
    elif tool_name == "generate_jenkins_pipeline":
        if "name" in validated:
            validated["name"] = validate_k8s_identifier(validated["name"], "name")
        if "languages" in validated:
            validated["languages"] = validate_languages(validated["languages"])

    # Tool: generate_gitlab_ci_pipeline
    elif tool_name == "generate_gitlab_ci_pipeline":
        if "name" in validated:
            validated["name"] = validate_k8s_identifier(validated["name"], "name")
        if "languages" in validated:
            validated["languages"] = validate_languages(validated["languages"])

    # Tool: generate_k8s_config
    elif tool_name == "generate_k8s_config":
        if "app_name" in validated:
            validated["app_name"] = validate_k8s_identifier(validated["app_name"], "app_name")
        if "image" in validated:
            validated["image"] = validate_image_reference(validated["image"])
        if "replicas" in validated:
            validated["replicas"] = validate_replica_count(validated["replicas"])
        if "port" in validated:
            validated["port"] = validate_port(validated["port"], "port")

    # Tool: generate_argocd_config
    elif tool_name == "generate_argocd_config":
        if "name" in validated:
            validated["name"] = validate_k8s_identifier(validated["name"], "name")
        if "namespace" in validated:
            validated["namespace"] = validate_k8s_identifier(validated["namespace"], "namespace")
        if "image" in validated:
            validated["image"] = validate_image_reference(validated["image"])
        if "repo" in validated:
            # Don't validate as absolute URL to avoid network calls
            validated["repo"] = validate_string_length(validated["repo"], "repo", max_len=512)

    # Tool: generate_sre_configs
    elif tool_name == "generate_sre_configs":
        if "name" in validated:
            validated["name"] = validate_k8s_identifier(validated["name"], "name")
        if "namespace" in validated:
            validated["namespace"] = validate_k8s_identifier(validated["namespace"], "namespace")
        if "team" in validated:
            validated["team"] = validate_k8s_identifier(validated["team"], "team")
        if "slo_target" in validated:
            validated["slo_target"] = validate_slo_target(validated["slo_target"])

    # Tool: scaffold_devcontainer
    elif tool_name == "scaffold_devcontainer":
        if "languages" in validated and validated["languages"]:
            validated["languages"] = validate_languages(validated["languages"])

    # Tool: generate_unittest_config
    elif tool_name == "generate_unittest_config":
        if "project_name" in validated:
            validated["project_name"] = validate_k8s_identifier(validated["project_name"], "project_name")
        if "languages" in validated:
            validated["languages"] = validate_languages(validated["languages"])

    return validated
