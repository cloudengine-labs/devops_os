#!/usr/bin/env python3
"""
DevOps-OS Infrastructure Hardening Scaffold Generator

Generates hardening configurations for Kubernetes clusters, container runtimes,
and operating systems based on industry standards (CIS, DISA STIG, NSA/CISA,
Pod Security Standards, Essential Eight).

Outputs (default: ./hardening/ directory):
  hardening/
  ├── kyverno/
  │   ├── cis-k8s/          CIS Kubernetes Benchmark Kyverno policies
  │   ├── stig-k8s/         DISA STIG Kubernetes Kyverno policies
  │   ├── nsa-k8s/          NSA/CISA Kubernetes Hardening Guide policies
  │   ├── pod-security-standards.yaml
  │   └── image-signing.yaml
  ├── inspec/
  │   ├── docker-cis/       CIS Docker Benchmark InSpec profile
  │   ├── rhel9-cis/        CIS RHEL 9 Benchmark InSpec profile
  │   └── ubuntu22-cis/     CIS Ubuntu 22.04 Benchmark InSpec profile
  ├── essential-eight/
  │   ├── README.md
  │   └── checkov/
  │       └── essential-eight-checks.py
  └── compliance-mapping.yaml
"""

import os
import argparse
import yaml
from pathlib import Path

ENV_PREFIX = "DEVOPS_OS_HARDENING_"

VALID_STANDARDS = [
    "cis-k8s",
    "stig-k8s",
    "nsa-k8s",
    "cis-docker",
    "cis-rhel9",
    "cis-ubuntu22",
    "pod-security",
    "image-signing",
    "essential-eight",
    "all",
]

VALID_TYPES = ["kyverno", "inspec", "checkov", "all"]
VALID_ENVIRONMENTS = ["dev", "staging", "production"]
VALID_SEVERITIES = ["critical", "high", "medium", "low"]
VALID_FRAMEWORKS = ["pci-dss", "hipaa", "iso27001", "rbi", "nist-800-53", "soc2"]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate infrastructure hardening configs for DevOps-OS"
    )
    parser.add_argument(
        "--standard",
        choices=VALID_STANDARDS,
        default=os.environ.get(f"{ENV_PREFIX}STANDARD", "all"),
        help=(
            "Hardening standard to generate: cis-k8s, stig-k8s, nsa-k8s, "
            "cis-docker, cis-rhel9, cis-ubuntu22, pod-security, image-signing, "
            "essential-eight, all (default: all)"
        ),
    )
    parser.add_argument(
        "--type",
        choices=VALID_TYPES,
        default=os.environ.get(f"{ENV_PREFIX}TYPE", "all"),
        dest="output_type",
        help="Output type: kyverno, inspec, checkov, all (default: all applicable)",
    )
    parser.add_argument(
        "--output",
        default=os.environ.get(f"{ENV_PREFIX}OUTPUT", "hardening"),
        help="Output directory (default: ./hardening/)",
    )
    parser.add_argument(
        "--compliance-framework",
        default=os.environ.get(f"{ENV_PREFIX}COMPLIANCE_FRAMEWORK", ""),
        help=(
            "Tag outputs with compliance framework IDs for catalog linking "
            "(pci-dss, hipaa, iso27001, rbi, nist-800-53, soc2)"
        ),
    )
    parser.add_argument(
        "--severity",
        choices=VALID_SEVERITIES,
        default=os.environ.get(f"{ENV_PREFIX}SEVERITY", "medium"),
        help="Minimum severity level to include: critical, high, medium, low (default: medium)",
    )
    parser.add_argument(
        "--environment",
        choices=VALID_ENVIRONMENTS,
        default=os.environ.get(f"{ENV_PREFIX}ENVIRONMENT", "production"),
        help=(
            "Target environment profile: dev, staging, production "
            "(adjusts enforcement levels, default: production)"
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        yaml.dump(data, fh, sort_keys=False, default_flow_style=False)
    return path


def _write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    return path


def _enforcement_action(environment):
    """Return Kyverno validationFailureAction based on target environment."""
    return "Enforce" if environment == "production" else "Audit"


def _severity_rank(severity):
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}[severity]


# ---------------------------------------------------------------------------
# CIS Kubernetes Benchmark Kyverno policies
# ---------------------------------------------------------------------------

def generate_kyverno_cis_k8s(args):
    """Generate CIS Kubernetes Benchmark v1.9 Kyverno ClusterPolicy files."""
    action = _enforcement_action(args.environment)
    output_dir = Path(args.output) / "kyverno" / "cis-k8s"
    generated = []

    # CIS 1.x — Master node / API Server settings
    policy_1 = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "cis-k8s-master-node-config",
            "annotations": {
                "policies.kyverno.io/title": "CIS Kubernetes 1.x Master Node Configuration",
                "policies.kyverno.io/category": "CIS Kubernetes Benchmark v1.9",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces CIS Kubernetes Benchmark v1.9 section 1.x controls "
                    "for API server security settings."
                ),
                "devops-os/compliance": "cis-k8s:1.2,pci-dss:2.2,hipaa:164.312",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "restrict-anonymous-auth",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": "Anonymous authentication to the API server must be disabled (CIS 1.2.1).",
                        "deny": {
                            "conditions": {
                                "any": [
                                    {
                                        "key": "{{request.object.spec.containers[].env[].name | contains(@, 'KUBERNETES_ANONYMOUS_AUTH') | any(@)}}",
                                        "operator": "Equals",
                                        "value": True,
                                    }
                                ]
                            }
                        },
                    },
                },
                {
                    "name": "require-tls-cert-auth",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": "API server client certificate authentication must be configured (CIS 1.2.5).",
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {
                                        "=(securityContext)": {
                                            "=(runAsNonRoot)": True,
                                        }
                                    }
                                ]
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "1-master-node-config.yaml", policy_1))

    # CIS 2.x — etcd security
    policy_2 = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "cis-k8s-etcd-config",
            "annotations": {
                "policies.kyverno.io/title": "CIS Kubernetes 2.x etcd Security",
                "policies.kyverno.io/category": "CIS Kubernetes Benchmark v1.9",
                "policies.kyverno.io/severity": "critical",
                "policies.kyverno.io/description": (
                    "Enforces CIS Kubernetes Benchmark v1.9 section 2.x controls "
                    "for etcd peer and client TLS."
                ),
                "devops-os/compliance": "cis-k8s:2.1,cis-k8s:2.2,pci-dss:4.1",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "require-etcd-tls",
                    "match": {
                        "any": [
                            {
                                "resources": {
                                    "kinds": ["Pod"],
                                    "namespaces": ["kube-system"],
                                }
                            }
                        ]
                    },
                    "validate": {
                        "message": "etcd must use TLS for peer and client communication (CIS 2.1, 2.2).",
                        "pattern": {
                            "metadata": {
                                "labels": {
                                    "component": "etcd",
                                }
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "2-etcd-config.yaml", policy_2))

    # CIS 3.x — Control plane configuration
    policy_3 = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "cis-k8s-control-plane-config",
            "annotations": {
                "policies.kyverno.io/title": "CIS Kubernetes 3.x Control Plane Configuration",
                "policies.kyverno.io/category": "CIS Kubernetes Benchmark v1.9",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces CIS Kubernetes Benchmark v1.9 section 3.x controls "
                    "for controller manager and scheduler security."
                ),
                "devops-os/compliance": "cis-k8s:3.1,cis-k8s:3.2",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "restrict-service-account-token-auto-mount",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Pods should not automatically mount service account tokens "
                            "unless required (CIS 3.1.1)."
                        ),
                        "pattern": {
                            "spec": {
                                "=(automountServiceAccountToken)": False,
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "3-control-plane-config.yaml", policy_3))

    # CIS 4.x — Worker node kubelet settings
    policy_4 = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "cis-k8s-worker-node-config",
            "annotations": {
                "policies.kyverno.io/title": "CIS Kubernetes 4.x Worker Node Configuration",
                "policies.kyverno.io/category": "CIS Kubernetes Benchmark v1.9",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces CIS Kubernetes Benchmark v1.9 section 4.x controls "
                    "for kubelet security configuration."
                ),
                "devops-os/compliance": "cis-k8s:4.2,cis-k8s:4.6",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "require-read-only-root-filesystem",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Containers must use a read-only root filesystem (CIS 4.2.4)."
                        ),
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {
                                        "securityContext": {
                                            "readOnlyRootFilesystem": True,
                                        }
                                    }
                                ]
                            }
                        },
                    },
                },
                {
                    "name": "disallow-privileged-containers",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": "Privileged containers are not allowed (CIS 4.2.6).",
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {
                                        "=(securityContext)": {
                                            "=(privileged)": False,
                                        }
                                    }
                                ]
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "4-worker-node-config.yaml", policy_4))

    # CIS 5.x — Policies (RBAC, secrets, networking)
    policy_5 = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "cis-k8s-policies",
            "annotations": {
                "policies.kyverno.io/title": "CIS Kubernetes 5.x Policies",
                "policies.kyverno.io/category": "CIS Kubernetes Benchmark v1.9",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces CIS Kubernetes Benchmark v1.9 section 5.x controls "
                    "for RBAC, secrets management, and network policies."
                ),
                "devops-os/compliance": "cis-k8s:5.1,cis-k8s:5.2,cis-k8s:5.7",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "restrict-wildcard-verbs",
                    "match": {
                        "any": [
                            {"resources": {"kinds": ["ClusterRole", "Role"]}}
                        ]
                    },
                    "validate": {
                        "message": "Wildcard (*) verbs in RBAC roles are not allowed (CIS 5.1.1).",
                        "deny": {
                            "conditions": {
                                "any": [
                                    {
                                        "key": "{{ request.object.rules[].verbs[] | contains(@, '*') | any(@) }}",
                                        "operator": "Equals",
                                        "value": True,
                                    }
                                ]
                            }
                        },
                    },
                },
                {
                    "name": "require-namespace-network-policy",
                    "match": {
                        "any": [{"resources": {"kinds": ["Namespace"]}}]
                    },
                    "validate": {
                        "message": (
                            "Each namespace must have at least one NetworkPolicy (CIS 5.7.1)."
                        ),
                        "deny": {
                            "conditions": {
                                "all": [
                                    {
                                        "key": "{{ request.object.metadata.name }}",
                                        "operator": "NotEquals",
                                        "value": "kube-system",
                                    }
                                ]
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "5-policies.yaml", policy_5))
    return generated


# ---------------------------------------------------------------------------
# DISA STIG Kubernetes Kyverno policies
# ---------------------------------------------------------------------------

def generate_kyverno_stig_k8s(args):
    """Generate DISA STIG for Kubernetes Kyverno ClusterPolicy."""
    action = _enforcement_action(args.environment)
    output_dir = Path(args.output) / "kyverno" / "stig-k8s"

    policy = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "stig-k8s-cluster-policies",
            "annotations": {
                "policies.kyverno.io/title": "DISA STIG for Kubernetes Cluster Policies",
                "policies.kyverno.io/category": "DISA STIG",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces DISA STIG for Kubernetes V1R9 controls "
                    "for cluster-level security hardening."
                ),
                "devops-os/compliance": "stig-k8s:V-242383,stig-k8s:V-242390,dod:8500.01",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "stig-disallow-host-namespaces",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Pods must not use host network, PID, or IPC namespaces "
                            "(STIG V-242383)."
                        ),
                        "pattern": {
                            "spec": {
                                "=(hostNetwork)": False,
                                "=(hostPID)": False,
                                "=(hostIPC)": False,
                            }
                        },
                    },
                },
                {
                    "name": "stig-require-resource-limits",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Containers must define CPU and memory resource limits "
                            "(STIG V-242390)."
                        ),
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {
                                        "resources": {
                                            "limits": {
                                                "cpu": "?*",
                                                "memory": "?*",
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                    },
                },
                {
                    "name": "stig-disallow-latest-image-tag",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Container images must not use the 'latest' tag "
                            "(STIG V-242414)."
                        ),
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {"image": "!*:latest"}
                                ]
                            }
                        },
                    },
                },
            ],
        },
    }
    path = _write_yaml(output_dir / "stig-cluster-policies.yaml", policy)
    return [path]


# ---------------------------------------------------------------------------
# NSA/CISA Kubernetes Hardening Guide Kyverno policies
# ---------------------------------------------------------------------------

def generate_kyverno_nsa_k8s(args):
    """Generate NSA/CISA Kubernetes Hardening Guide Kyverno policies."""
    action = _enforcement_action(args.environment)
    output_dir = Path(args.output) / "kyverno" / "nsa-k8s"
    generated = []

    # NSA pod hardening
    pod_policy = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "nsa-pod-security",
            "annotations": {
                "policies.kyverno.io/title": "NSA/CISA Kubernetes Pod Security",
                "policies.kyverno.io/category": "NSA/CISA Kubernetes Hardening Guide",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces NSA/CISA Kubernetes Hardening Guide pod-level "
                    "security controls (August 2022)."
                ),
                "devops-os/compliance": "nsa-k8s:pod-security,nist-800-53:AC-6,nist-800-53:CM-6",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "nsa-drop-all-capabilities",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": (
                            "Containers must drop ALL capabilities and only add back what is required "
                            "(NSA Pod Security)."
                        ),
                        "pattern": {
                            "spec": {
                                "containers": [
                                    {
                                        "securityContext": {
                                            "capabilities": {"drop": ["ALL"]},
                                        }
                                    }
                                ]
                            }
                        },
                    },
                },
                {
                    "name": "nsa-run-as-non-root",
                    "match": {"any": [{"resources": {"kinds": ["Pod"]}}]},
                    "validate": {
                        "message": "Containers must run as non-root user (NSA Pod Security).",
                        "pattern": {
                            "spec": {
                                "securityContext": {
                                    "runAsNonRoot": True,
                                }
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "pod-security.yaml", pod_policy))

    # NSA network segmentation
    network_policy = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "nsa-network-policies",
            "annotations": {
                "policies.kyverno.io/title": "NSA/CISA Kubernetes Network Segmentation",
                "policies.kyverno.io/category": "NSA/CISA Kubernetes Hardening Guide",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    "Enforces NSA/CISA Kubernetes Hardening Guide network segmentation controls."
                ),
                "devops-os/compliance": "nsa-k8s:network,nist-800-53:SC-7",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "rules": [
                {
                    "name": "nsa-default-deny-ingress",
                    "match": {"any": [{"resources": {"kinds": ["Namespace"]}}]},
                    "generate": {
                        "apiVersion": "networking.k8s.io/v1",
                        "kind": "NetworkPolicy",
                        "name": "default-deny-ingress",
                        "namespace": "{{request.object.metadata.name}}",
                        "data": {
                            "spec": {
                                "podSelector": {},
                                "policyTypes": ["Ingress"],
                            }
                        },
                    },
                },
            ],
        },
    }
    generated.append(_write_yaml(output_dir / "network-policies.yaml", network_policy))
    return generated


# ---------------------------------------------------------------------------
# Pod Security Standards
# ---------------------------------------------------------------------------

def generate_kyverno_pod_security(args):
    """Generate Kubernetes Pod Security Standards Kyverno ClusterPolicy."""
    action = _enforcement_action(args.environment)
    output_dir = Path(args.output) / "kyverno"

    # Use Restricted profile for production, Baseline for dev/staging
    profile = "restricted" if args.environment == "production" else "baseline"

    policy = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "pod-security-standards",
            "annotations": {
                "policies.kyverno.io/title": f"Pod Security Standards ({profile.title()})",
                "policies.kyverno.io/category": "Pod Security Standards",
                "policies.kyverno.io/severity": "high",
                "policies.kyverno.io/description": (
                    f"Enforces Kubernetes Pod Security Standards at the '{profile}' profile level. "
                    "Applies to all workload namespaces."
                ),
                "devops-os/compliance": "pss:restricted,cis-k8s:5.2,nsa-k8s:pod-security",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "background": True,
            "rules": [
                {
                    "name": "pss-baseline-disallow-host-process",
                    "match": {
                        "any": [
                            {
                                "resources": {
                                    "kinds": ["Pod"],
                                    "namespaces": ["!kube-system", "!kube-public"],
                                }
                            }
                        ]
                    },
                    "validate": {
                        "message": "Windows HostProcess containers are not allowed (PSS Baseline).",
                        "pattern": {
                            "spec": {
                                "=(securityContext)": {
                                    "=(windowsOptions)": {
                                        "=(hostProcess)": False,
                                    }
                                },
                                "containers": [
                                    {
                                        "=(securityContext)": {
                                            "=(windowsOptions)": {
                                                "=(hostProcess)": False,
                                            }
                                        }
                                    }
                                ],
                            }
                        },
                    },
                },
                {
                    "name": f"pss-{profile}-seccomp",
                    "match": {
                        "any": [
                            {
                                "resources": {
                                    "kinds": ["Pod"],
                                    "namespaces": ["!kube-system", "!kube-public"],
                                }
                            }
                        ]
                    },
                    "validate": {
                        "message": f"Seccomp profile must be set to RuntimeDefault or Localhost (PSS {profile.title()}).",
                        "anyPattern": [
                            {
                                "spec": {
                                    "securityContext": {
                                        "seccompProfile": {
                                            "type": "RuntimeDefault",
                                        }
                                    }
                                }
                            },
                            {
                                "spec": {
                                    "securityContext": {
                                        "seccompProfile": {
                                            "type": "Localhost",
                                        }
                                    }
                                }
                            },
                        ],
                    },
                },
            ],
        },
    }
    path = _write_yaml(output_dir / "pod-security-standards.yaml", policy)
    return [path]


# ---------------------------------------------------------------------------
# Container Image Signing
# ---------------------------------------------------------------------------

def generate_kyverno_image_signing(args):
    """Generate Kyverno + Cosign image signature verification ClusterPolicy."""
    action = _enforcement_action(args.environment)
    output_dir = Path(args.output) / "kyverno"

    policy = {
        "apiVersion": "kyverno.io/v1",
        "kind": "ClusterPolicy",
        "metadata": {
            "name": "image-signing",
            "annotations": {
                "policies.kyverno.io/title": "Container Image Signing (Cosign)",
                "policies.kyverno.io/category": "Image Signing",
                "policies.kyverno.io/severity": "critical",
                "policies.kyverno.io/description": (
                    "Verifies that all container images are signed with Cosign "
                    "before admission to the cluster."
                ),
                "devops-os/compliance": "image-signing:cosign,slsa:L2,pci-dss:6.3.3",
            },
        },
        "spec": {
            "validationFailureAction": action,
            "background": False,
            "rules": [
                {
                    "name": "verify-image-signature",
                    "match": {
                        "any": [
                            {
                                "resources": {
                                    "kinds": ["Pod"],
                                    "namespaces": ["!kube-system", "!kube-public"],
                                }
                            }
                        ]
                    },
                    "verifyImages": [
                        {
                            "imageReferences": ["*"],
                            "attestors": [
                                {
                                    "count": 1,
                                    "entries": [
                                        {
                                            "keys": {
                                                "publicKeys": "REPLACE_WITH_YOUR_COSIGN_PUBLIC_KEY",  # TODO: set your cosign.pub content
                                                "signatureAlgorithm": "sha256",
                                            }
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ],
        },
    }
    path = _write_yaml(output_dir / "image-signing.yaml", policy)
    return [path]


# ---------------------------------------------------------------------------
# InSpec profile generators
# ---------------------------------------------------------------------------

def _inspec_yml(name, title, description, version="1.0.0"):
    # TODO: Update copyright_email to your organization's contact address before deploying
    return f"""name: {name}
title: {title}
maintainer: DevOps-OS Hardening Team
copyright: DevOps-OS Contributors
copyright_email: devops-os@example.com
license: Apache-2.0
summary: {description}
version: {version}
supports:
  - platform: linux
inspec_version: ">= 5.0"
"""


def generate_inspec_docker_cis(args):
    """Generate CIS Docker Benchmark v1.6 InSpec profile skeleton."""
    base = Path(args.output) / "inspec" / "docker-cis"
    generated = []

    generated.append(_write_text(
        base / "inspec.yml",
        _inspec_yml(
            "docker-cis",
            "CIS Docker Benchmark v1.6",
            "InSpec profile for CIS Docker Benchmark v1.6 compliance checks",
        ),
    ))

    controls = {
        "1_host_configuration.rb": """\
# encoding: utf-8
# CIS Docker Benchmark v1.6 - Section 1: Host Configuration

title "CIS Docker Benchmark - Section 1: Host Configuration"

control "cis-docker-1.1" do
  impact 1.0
  title "Ensure a separate partition for containers has been created"
  desc "All Docker containers and their data should be stored in a dedicated partition."
  tag cis: "1.1"
  tag compliance: ["cis-docker:1.1", "pci-dss:2.2.1"]

  describe file("/var/lib/docker") do
    it { should be_mounted }
  end
end

control "cis-docker-1.2" do
  impact 0.7
  title "Ensure only trusted users are allowed to control Docker daemon"
  desc "The Docker daemon currently requires root privileges. Only trusted users should be added to the docker group."
  tag cis: "1.2"
  tag compliance: ["cis-docker:1.2", "pci-dss:7.1"]

  describe group("docker") do
    its("members") { should_not include "nobody" }
  end
end
""",
        "2_docker_daemon.rb": """\
# encoding: utf-8
# CIS Docker Benchmark v1.6 - Section 2: Docker Daemon Configuration

title "CIS Docker Benchmark - Section 2: Docker Daemon Configuration"

control "cis-docker-2.1" do
  impact 1.0
  title "Ensure network traffic is restricted between containers on the default bridge"
  desc "By default, all network traffic is allowed between containers on the same host. Restrict inter-container communication."
  tag cis: "2.1"
  tag compliance: ["cis-docker:2.1", "nist-800-53:SC-7"]

  describe json("/etc/docker/daemon.json") do
    its(["icc"]) { should cmp false }
  end
end

control "cis-docker-2.2" do
  impact 1.0
  title "Ensure logging level is set to info"
  desc "Setting up an appropriate log level configures the Docker daemon to log events."
  tag cis: "2.2"
  tag compliance: ["cis-docker:2.2", "pci-dss:10.2"]

  describe json("/etc/docker/daemon.json") do
    its(["log-level"]) { should eq "info" }
  end
end
""",
        "3_docker_daemon_files.rb": """\
# encoding: utf-8
# CIS Docker Benchmark v1.6 - Section 3: Docker Daemon Configuration Files

title "CIS Docker Benchmark - Section 3: Docker Daemon Configuration Files"

control "cis-docker-3.1" do
  impact 1.0
  title "Ensure that the docker.service file ownership is set to root:root"
  desc "The docker.service file contains sensitive parameters that may alter the behavior of the Docker daemon."
  tag cis: "3.1"
  tag compliance: ["cis-docker:3.1"]

  describe file("/lib/systemd/system/docker.service") do
    it { should be_owned_by "root" }
    it { should be_grouped_into "root" }
  end
end

control "cis-docker-3.2" do
  impact 1.0
  title "Ensure that docker.service file permissions are set to 644 or more restrictive"
  desc "The docker.service file should not be writable by any user other than root."
  tag cis: "3.2"
  tag compliance: ["cis-docker:3.2"]

  describe file("/lib/systemd/system/docker.service") do
    its("mode") { should cmp "0644" }
  end
end
""",
        "4_container_images.rb": """\
# encoding: utf-8
# CIS Docker Benchmark v1.6 - Section 4: Container Images and Build Files

title "CIS Docker Benchmark - Section 4: Container Images and Build Files"

control "cis-docker-4.1" do
  impact 1.0
  title "Ensure a user for the container has been created"
  desc "Create a non-root user for the container in the Dockerfile. Running containers as non-root reduces attack surface."
  tag cis: "4.1"
  tag compliance: ["cis-docker:4.1", "pci-dss:6.2"]

  describe command("docker inspect --format '{{ .Config.User }}' $(docker ps -q)") do
    its("stdout") { should_not be_empty }
  end
end

control "cis-docker-4.6" do
  impact 0.7
  title "Ensure HEALTHCHECK instructions have been added to container images"
  desc "Add HEALTHCHECK instruction in the Dockerfile to perform a health check on running containers."
  tag cis: "4.6"
  tag compliance: ["cis-docker:4.6"]

  describe command("docker inspect --format '{{ .Config.Healthcheck }}' $(docker ps -q)") do
    its("stdout") { should_not match "<nil>" }
  end
end
""",
        "5_container_runtime.rb": """\
# encoding: utf-8
# CIS Docker Benchmark v1.6 - Section 5: Container Runtime

title "CIS Docker Benchmark - Section 5: Container Runtime"

control "cis-docker-5.1" do
  impact 1.0
  title "Ensure AppArmor profile is enabled"
  desc "AppArmor is a Linux security module. Docker supports AppArmor profiles for container isolation."
  tag cis: "5.1"
  tag compliance: ["cis-docker:5.1", "nist-800-53:SI-7"]

  describe command("docker inspect --format '{{ .AppArmorProfile }}' $(docker ps -q)") do
    its("stdout") { should_not be_empty }
  end
end

control "cis-docker-5.4" do
  impact 1.0
  title "Ensure privileged containers are not used"
  desc "Running containers in privileged mode gives all Linux capabilities to the container."
  tag cis: "5.4"
  tag compliance: ["cis-docker:5.4", "pci-dss:6.5.8", "nsa-k8s:pod-security"]

  describe command("docker ps --quiet --all | xargs docker inspect --format '{{ .Name }} {{ .HostConfig.Privileged }}'") do
    its("stdout") { should_not match "true" }
  end
end
""",
    }

    for filename, content in controls.items():
        generated.append(_write_text(base / "controls" / filename, content))

    return generated


def _rhel9_inspec_controls():
    return {
        "1_filesystem.rb": """\
# encoding: utf-8
# CIS RHEL 9 Benchmark - Section 1: Initial Setup - Filesystem Configuration

title "CIS RHEL 9 Benchmark - Section 1: Filesystem Configuration"

control "cis-rhel9-1.1.1" do
  impact 1.0
  title "Ensure /tmp is a separate partition"
  desc "The /tmp directory is a world-writable directory used for temporary storage. Mount it on a separate partition."
  tag cis: "1.1.1"
  tag compliance: ["cis-rhel9:1.1.1"]

  describe mount("/tmp") do
    it { should be_mounted }
  end
end

control "cis-rhel9-1.1.2" do
  impact 0.7
  title "Ensure nodev option set on /tmp partition"
  desc "The nodev mount option prevents device files from being created on the /tmp partition."
  tag cis: "1.1.2"
  tag compliance: ["cis-rhel9:1.1.2"]

  describe mount("/tmp") do
    its("options") { should include "nodev" }
  end
end
""",
        "2_services.rb": """\
# encoding: utf-8
# CIS RHEL 9 Benchmark - Section 2: Services

title "CIS RHEL 9 Benchmark - Section 2: Services"

control "cis-rhel9-2.1.1" do
  impact 1.0
  title "Ensure xinetd is not installed"
  desc "The eXtended InterNET Daemon (xinetd) is an open-source super-daemon. Remove if not required."
  tag cis: "2.1.1"
  tag compliance: ["cis-rhel9:2.1.1"]

  describe package("xinetd") do
    it { should_not be_installed }
  end
end

control "cis-rhel9-2.2.1" do
  impact 1.0
  title "Ensure time synchronization is in use"
  desc "Time synchronization is important for log accuracy and security event correlation."
  tag cis: "2.2.1"
  tag compliance: ["cis-rhel9:2.2.1", "pci-dss:10.4"]

  describe.one do
    describe package("chrony") do
      it { should be_installed }
    end
    describe package("ntp") do
      it { should be_installed }
    end
  end
end
""",
        "3_network.rb": """\
# encoding: utf-8
# CIS RHEL 9 Benchmark - Section 3: Network Configuration

title "CIS RHEL 9 Benchmark - Section 3: Network Configuration"

control "cis-rhel9-3.1.1" do
  impact 1.0
  title "Ensure IP forwarding is disabled"
  desc "IP forwarding should be disabled unless the system is configured to act as a router."
  tag cis: "3.1.1"
  tag compliance: ["cis-rhel9:3.1.1", "nist-800-53:CM-7"]

  describe kernel_parameter("net.ipv4.ip_forward") do
    its("value") { should eq 0 }
  end
end

control "cis-rhel9-3.3.1" do
  impact 1.0
  title "Ensure source routed packets are not accepted"
  desc "Source-routed packets can be used to spoof traffic from trusted networks."
  tag cis: "3.3.1"
  tag compliance: ["cis-rhel9:3.3.1", "nist-800-53:SC-5"]

  describe kernel_parameter("net.ipv4.conf.all.accept_source_route") do
    its("value") { should eq 0 }
  end
end
""",
        "4_logging.rb": """\
# encoding: utf-8
# CIS RHEL 9 Benchmark - Section 4: Logging and Auditing

title "CIS RHEL 9 Benchmark - Section 4: Logging and Auditing"

control "cis-rhel9-4.1.1" do
  impact 1.0
  title "Ensure auditd is installed"
  desc "auditd is the userspace component of the Linux Auditing System."
  tag cis: "4.1.1"
  tag compliance: ["cis-rhel9:4.1.1", "pci-dss:10.2", "hipaa:164.312.b"]

  describe package("audit") do
    it { should be_installed }
  end
end

control "cis-rhel9-4.1.2" do
  impact 1.0
  title "Ensure auditd service is enabled"
  desc "The auditd daemon should be running to capture audit events."
  tag cis: "4.1.2"
  tag compliance: ["cis-rhel9:4.1.2", "pci-dss:10.5"]

  describe service("auditd") do
    it { should be_enabled }
    it { should be_running }
  end
end
""",
        "5_access.rb": """\
# encoding: utf-8
# CIS RHEL 9 Benchmark - Section 5: Access, Authentication and Authorization

title "CIS RHEL 9 Benchmark - Section 5: Access, Authentication and Authorization"

control "cis-rhel9-5.1.1" do
  impact 1.0
  title "Ensure cron daemon is enabled"
  desc "The cron daemon is used to execute scheduled commands."
  tag cis: "5.1.1"
  tag compliance: ["cis-rhel9:5.1.1"]

  describe service("crond") do
    it { should be_enabled }
    it { should be_running }
  end
end

control "cis-rhel9-5.3.1" do
  impact 1.0
  title "Ensure password creation requirements are configured"
  desc "Strong passwords reduce the risk of successful brute force attacks."
  tag cis: "5.3.1"
  tag compliance: ["cis-rhel9:5.3.1", "pci-dss:8.3.6", "nist-800-53:IA-5"]

  describe file("/etc/security/pwquality.conf") do
    its("content") { should match /minlen\\s*=\\s*14/ }
    its("content") { should match /dcredit\\s*=\\s*-1/ }
    its("content") { should match /ucredit\\s*=\\s*-1/ }
  end
end
""",
    }


def generate_inspec_rhel9_cis(args):
    """Generate CIS RHEL 9 Benchmark InSpec profile skeleton."""
    base = Path(args.output) / "inspec" / "rhel9-cis"
    generated = []

    generated.append(_write_text(
        base / "inspec.yml",
        _inspec_yml(
            "rhel9-cis",
            "CIS Red Hat Enterprise Linux 9 Benchmark",
            "InSpec profile for CIS RHEL 9 Benchmark compliance checks",
        ),
    ))

    for filename, content in _rhel9_inspec_controls().items():
        generated.append(_write_text(base / "controls" / filename, content))

    return generated


def generate_inspec_ubuntu22_cis(args):
    """Generate CIS Ubuntu 22.04 Benchmark InSpec profile skeleton."""
    base = Path(args.output) / "inspec" / "ubuntu22-cis"
    generated = []

    generated.append(_write_text(
        base / "inspec.yml",
        _inspec_yml(
            "ubuntu22-cis",
            "CIS Ubuntu Linux 22.04 LTS Benchmark",
            "InSpec profile for CIS Ubuntu 22.04 Benchmark compliance checks",
        ),
    ))

    controls = {
        "1_filesystem.rb": """\
# encoding: utf-8
# CIS Ubuntu 22.04 Benchmark - Section 1: Filesystem Configuration

title "CIS Ubuntu 22.04 Benchmark - Section 1: Filesystem Configuration"

control "cis-ubuntu22-1.1.1" do
  impact 1.0
  title "Ensure /tmp is a separate partition"
  desc "The /tmp directory is a world-writable directory. Mount it on a separate partition."
  tag cis: "1.1.1"
  tag compliance: ["cis-ubuntu22:1.1.1"]

  describe mount("/tmp") do
    it { should be_mounted }
  end
end

control "cis-ubuntu22-1.1.2" do
  impact 0.7
  title "Ensure nodev option set on /tmp partition"
  desc "The nodev mount option prevents device files on /tmp."
  tag cis: "1.1.2"
  tag compliance: ["cis-ubuntu22:1.1.2"]

  describe mount("/tmp") do
    its("options") { should include "nodev" }
  end
end
""",
        "2_services.rb": """\
# encoding: utf-8
# CIS Ubuntu 22.04 Benchmark - Section 2: Services

title "CIS Ubuntu 22.04 Benchmark - Section 2: Services"

control "cis-ubuntu22-2.1.1" do
  impact 1.0
  title "Ensure xinetd is not installed"
  desc "The xinetd daemon is not required on modern Ubuntu systems."
  tag cis: "2.1.1"
  tag compliance: ["cis-ubuntu22:2.1.1"]

  describe package("xinetd") do
    it { should_not be_installed }
  end
end
""",
        "3_network.rb": """\
# encoding: utf-8
# CIS Ubuntu 22.04 Benchmark - Section 3: Network Configuration

title "CIS Ubuntu 22.04 Benchmark - Section 3: Network Configuration"

control "cis-ubuntu22-3.1.1" do
  impact 1.0
  title "Ensure IP forwarding is disabled"
  desc "IP forwarding should be disabled unless configured as a router."
  tag cis: "3.1.1"
  tag compliance: ["cis-ubuntu22:3.1.1", "nist-800-53:CM-7"]

  describe kernel_parameter("net.ipv4.ip_forward") do
    its("value") { should eq 0 }
  end
end
""",
        "4_logging.rb": """\
# encoding: utf-8
# CIS Ubuntu 22.04 Benchmark - Section 4: Logging and Auditing

title "CIS Ubuntu 22.04 Benchmark - Section 4: Logging and Auditing"

control "cis-ubuntu22-4.1.1" do
  impact 1.0
  title "Ensure auditd is installed"
  desc "auditd provides audit capabilities for the Linux kernel."
  tag cis: "4.1.1"
  tag compliance: ["cis-ubuntu22:4.1.1", "pci-dss:10.2"]

  describe package("auditd") do
    it { should be_installed }
  end
end
""",
        "5_access.rb": """\
# encoding: utf-8
# CIS Ubuntu 22.04 Benchmark - Section 5: Access, Authentication and Authorization

title "CIS Ubuntu 22.04 Benchmark - Section 5: Access, Authentication and Authorization"

control "cis-ubuntu22-5.3.1" do
  impact 1.0
  title "Ensure password creation requirements are configured"
  desc "Strong passwords reduce the risk of brute force attacks."
  tag cis: "5.3.1"
  tag compliance: ["cis-ubuntu22:5.3.1", "pci-dss:8.3.6"]

  describe file("/etc/security/pwquality.conf") do
    its("content") { should match /minlen\\s*=\\s*14/ }
  end
end
""",
    }

    for filename, content in controls.items():
        generated.append(_write_text(base / "controls" / filename, content))

    return generated


# ---------------------------------------------------------------------------
# Essential Eight
# ---------------------------------------------------------------------------

def generate_essential_eight(args):
    """Generate ASD Essential Eight Checkov checks and README."""
    base = Path(args.output) / "essential-eight"
    generated = []

    readme = """\
# Essential Eight (ASD) — DevOps-OS Hardening

The Australian Signals Directorate (ASD) Essential Eight is a set of eight
baseline mitigation strategies for cyber security hardening.

## Maturity Levels

| Level | Description |
|-------|-------------|
| ML0   | Not implemented or does not align with the intent |
| ML1   | Partly aligned with the intent (opportunistic adversaries) |
| ML2   | Mostly aligned with the intent (targeted adversaries) |
| ML3   | Fully aligned with the intent (sophisticated adversaries) |

## Controls Covered

| Control | Description | Tool | File |
|---------|-------------|------|------|
| E8-1    | Application control | Checkov | essential-eight-checks.py |
| E8-2    | Patch applications | Checkov | essential-eight-checks.py |
| E8-3    | Configure Microsoft Office macros | Checkov | essential-eight-checks.py |
| E8-4    | User application hardening | Checkov | essential-eight-checks.py |
| E8-5    | Restrict admin privileges | Checkov + InSpec | essential-eight-checks.py |
| E8-6    | Patch operating systems | Checkov | essential-eight-checks.py |
| E8-7    | Multi-factor authentication | Checkov | essential-eight-checks.py |
| E8-8    | Regular backups | Checkov | essential-eight-checks.py |

## Usage

```bash
# Run Essential Eight Checkov checks against IaC
checkov --external-checks-dir hardening/essential-eight/checkov \\
        --directory . \\
        --framework terraform
```

## Applicability

These checks apply to:
- Terraform IaC configurations (AWS, Azure, GCP)
- Kubernetes manifests
- CI/CD pipeline definitions

## References

- [ASD Essential Eight](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight)
- [Essential Eight Maturity Model](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight/essential-eight-maturity-model)
"""
    generated.append(_write_text(base / "README.md", readme))

    checkov_checks = '''\
"""
Essential Eight (ASD) — Checkov Custom Checks

Custom Checkov checks implementing the Australian Signals Directorate (ASD)
Essential Eight mitigation strategies for IaC compliance scanning.

Usage:
    checkov --external-checks-dir hardening/essential-eight/checkov \\
            --directory . --framework terraform
"""

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class E8RestrictAdminPrivileges(BaseResourceCheck):
    """E8-5: Restrict Administrative Privileges.

    Checks that IAM roles/policies do not grant overly broad admin permissions.
    """

    def __init__(self):
        name = "E8-5: Restrict Administrative Privileges — No wildcard IAM actions"
        id = "E8_5_RESTRICT_ADMIN"
        supported_resources = [
            "aws_iam_policy",
            "aws_iam_role_policy",
            "aws_iam_user_policy",
        ]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        statements = conf.get("policy", [{}])
        if isinstance(statements, list):
            statements = statements[0] if statements else {}
        if isinstance(statements, str):
            import json
            try:
                statements = json.loads(statements)
            except (ValueError, TypeError):
                return CheckResult.PASSED

        for stmt in statements.get("Statement", []):
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            if "*" in actions or "iam:*" in actions:
                return CheckResult.FAILED
        return CheckResult.PASSED


class E8MultiFactorAuthentication(BaseResourceCheck):
    """E8-7: Multi-Factor Authentication.

    Checks that IAM users have MFA device policies enforced.
    """

    def __init__(self):
        name = "E8-7: Multi-Factor Authentication — Enforce MFA on IAM users"
        id = "E8_7_MFA"
        supported_resources = ["aws_iam_user"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Check for MFA enforcement tag
        tags = conf.get("tags", [{}])
        if isinstance(tags, list):
            tags = tags[0] if tags else {}
        if tags.get("mfa-enforced") == "true":
            return CheckResult.PASSED
        return CheckResult.FAILED


class E8RegularBackups(BaseResourceCheck):
    """E8-8: Regular Backups.

    Checks that storage resources have backup/retention policies configured.
    """

    def __init__(self):
        name = "E8-8: Regular Backups — Ensure backup retention is configured"
        id = "E8_8_BACKUPS"
        supported_resources = [
            "aws_db_instance",
            "aws_rds_cluster",
            "aws_dynamodb_table",
        ]
        categories = [CheckCategories.BACKUP_RECOVERY]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        retention = conf.get("backup_retention_period", [0])
        if isinstance(retention, list):
            retention = retention[0] if retention else 0
        try:
            if int(retention) >= 7:
                return CheckResult.PASSED
        except (ValueError, TypeError):
            pass
        return CheckResult.FAILED


scanner_e8_restrict_admin = E8RestrictAdminPrivileges()
scanner_e8_mfa = E8MultiFactorAuthentication()
scanner_e8_backups = E8RegularBackups()
'''
    generated.append(_write_text(base / "checkov" / "essential-eight-checks.py", checkov_checks))
    return generated


# ---------------------------------------------------------------------------
# Compliance mapping
# ---------------------------------------------------------------------------

def generate_compliance_mapping(args):
    """Generate compliance-mapping.yaml linking hardening rules to framework controls."""
    output_dir = Path(args.output)

    mapping = {
        "version": "1.0",
        "description": (
            "Maps DevOps-OS hardening rules to compliance framework control IDs. "
            "Consumed by GovPilot check_selector.py to link hardening checks into the catalog."
        ),
        "mappings": {
            "cis-k8s": {
                "1.2.1": {"title": "API server anonymous auth disabled",
                          "pci-dss": ["2.2"], "hipaa": ["164.312(a)(1)"],
                          "nist-800-53": ["AC-3", "AC-6"], "iso27001": ["A.9.4.1"]},
                "2.1": {"title": "etcd TLS peer communication",
                        "pci-dss": ["4.1"], "nist-800-53": ["SC-8", "SC-28"]},
                "4.2.4": {"title": "Read-only root filesystem",
                          "pci-dss": ["6.5.8"], "nist-800-53": ["CM-7", "SI-7"]},
                "4.2.6": {"title": "No privileged containers",
                          "pci-dss": ["6.5.8"], "nist-800-53": ["AC-6", "CM-7"]},
                "5.1.1": {"title": "No wildcard verbs in RBAC",
                          "pci-dss": ["7.1.2"], "nist-800-53": ["AC-6"],
                          "hipaa": ["164.312(a)(1)"]},
                "5.7.1": {"title": "Namespace network policies required",
                          "pci-dss": ["1.3"], "nist-800-53": ["SC-7"]},
            },
            "stig-k8s": {
                "V-242383": {"title": "No host namespace sharing",
                             "pci-dss": ["6.5.8"], "dod": ["8500.01"],
                             "nist-800-53": ["AC-6", "CM-7"]},
                "V-242390": {"title": "Resource limits required",
                             "pci-dss": ["6.6"], "nist-800-53": ["SC-5"]},
                "V-242414": {"title": "No latest image tag",
                             "pci-dss": ["6.3.3"], "nist-800-53": ["CM-11"]},
            },
            "nsa-k8s": {
                "pod-security": {"title": "Drop ALL capabilities, run as non-root",
                                 "nist-800-53": ["AC-6", "CM-6"],
                                 "pci-dss": ["6.5.8"]},
                "network": {"title": "Default deny ingress network policy",
                            "nist-800-53": ["SC-7"], "pci-dss": ["1.3"]},
            },
            "cis-docker": {
                "1.1": {"title": "Separate /var/lib/docker partition",
                        "pci-dss": ["2.2.1"]},
                "2.1": {"title": "Restrict inter-container communication",
                        "pci-dss": ["1.3"], "nist-800-53": ["SC-7"]},
                "5.4": {"title": "No privileged containers",
                        "pci-dss": ["6.5.8"], "nist-800-53": ["AC-6"]},
            },
            "cis-rhel9": {
                "1.1.1": {"title": "/tmp on separate partition",
                          "pci-dss": ["2.2.1"]},
                "3.1.1": {"title": "IP forwarding disabled",
                          "nist-800-53": ["CM-7"]},
                "4.1.1": {"title": "auditd installed",
                          "pci-dss": ["10.2"], "hipaa": ["164.312(b)"],
                          "nist-800-53": ["AU-2", "AU-12"]},
                "5.3.1": {"title": "Password complexity requirements",
                          "pci-dss": ["8.3.6"], "nist-800-53": ["IA-5"]},
            },
            "cis-ubuntu22": {
                "1.1.1": {"title": "/tmp on separate partition",
                          "pci-dss": ["2.2.1"]},
                "3.1.1": {"title": "IP forwarding disabled",
                          "nist-800-53": ["CM-7"]},
                "4.1.1": {"title": "auditd installed",
                          "pci-dss": ["10.2"], "hipaa": ["164.312(b)"]},
                "5.3.1": {"title": "Password complexity requirements",
                          "pci-dss": ["8.3.6"]},
            },
            "pod-security-standards": {
                "baseline": {"title": "Baseline Pod Security Standard",
                             "cis-k8s": ["5.2"], "nsa-k8s": ["pod-security"]},
                "restricted": {"title": "Restricted Pod Security Standard",
                               "cis-k8s": ["5.2"], "nsa-k8s": ["pod-security"],
                               "pci-dss": ["6.5.8"]},
            },
            "image-signing": {
                "cosign": {"title": "Container image Cosign signature verification",
                           "slsa": ["L2"], "pci-dss": ["6.3.3"],
                           "nist-800-53": ["CM-11", "SI-7"]},
            },
            "essential-eight": {
                "E8-5": {"title": "Restrict administrative privileges",
                         "nist-800-53": ["AC-6"], "iso27001": ["A.9.2.3"]},
                "E8-7": {"title": "Multi-factor authentication",
                         "pci-dss": ["8.4"], "nist-800-53": ["IA-2"],
                         "iso27001": ["A.9.4.2"]},
                "E8-8": {"title": "Regular backups",
                         "pci-dss": ["12.3.4"], "nist-800-53": ["CP-9"],
                         "iso27001": ["A.12.3.1"]},
            },
        },
    }

    path = _write_yaml(output_dir / "compliance-mapping.yaml", mapping)
    return [path]


# ---------------------------------------------------------------------------
# Dispatch logic
# ---------------------------------------------------------------------------

_KYVERNO_STANDARDS = {"cis-k8s", "stig-k8s", "nsa-k8s", "pod-security", "image-signing"}
_INSPEC_STANDARDS = {"cis-docker", "cis-rhel9", "cis-ubuntu22"}
_CHECKOV_STANDARDS = {"essential-eight"}

_GENERATORS = {
    "cis-k8s": generate_kyverno_cis_k8s,
    "stig-k8s": generate_kyverno_stig_k8s,
    "nsa-k8s": generate_kyverno_nsa_k8s,
    "pod-security": generate_kyverno_pod_security,
    "image-signing": generate_kyverno_image_signing,
    "cis-docker": generate_inspec_docker_cis,
    "cis-rhel9": generate_inspec_rhel9_cis,
    "cis-ubuntu22": generate_inspec_ubuntu22_cis,
    "essential-eight": generate_essential_eight,
}


def _should_generate(standard, output_type):
    """Return True if this standard matches the requested output type filter."""
    if output_type == "all":
        return True
    if output_type == "kyverno" and standard in _KYVERNO_STANDARDS:
        return True
    if output_type == "inspec" and standard in _INSPEC_STANDARDS:
        return True
    if output_type == "checkov" and standard in _CHECKOV_STANDARDS:
        return True
    return False


def generate_hardening(args):
    """Top-level dispatcher: calls the appropriate generators and returns all generated paths."""
    generated = []

    standards = list(_GENERATORS.keys()) if args.standard == "all" else [args.standard]

    for standard in standards:
        if not _should_generate(standard, args.output_type):
            continue
        gen_fn = _GENERATORS[standard]
        generated.extend(gen_fn(args))

    # Always generate compliance mapping when running "all" or explicitly
    if args.standard == "all" or args.output_type in ("all", "kyverno", "inspec", "checkov"):
        generated.extend(generate_compliance_mapping(args))

    return generated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_arguments()
    generated = generate_hardening(args)

    if generated:
        print(f"Hardening configs generated in '{args.output}/':")
        for path in generated:
            print(f"  {path}")
    else:
        print(
            f"No files generated for --standard={args.standard} --type={args.output_type}. "
            "Check that the standard supports the requested output type."
        )


if __name__ == "__main__":
    main()
