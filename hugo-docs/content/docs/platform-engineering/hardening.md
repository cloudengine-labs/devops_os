---
title: "Infrastructure Hardening"
weight: 16
---

# Infrastructure Hardening

DevOps-OS includes `python -m cli.devopsos scaffold hardening` to generate reusable hardening baselines for Kubernetes clusters, container runtimes, and operating systems.

---

## What it generates

| Output type | Purpose | Default location |
|-------------|---------|------------------|
| Kyverno policies | Kubernetes admission guardrails for CIS, STIG, NSA/CISA, Pod Security Standards, image signing, and OWASP ASVS L1 | `hardening/kyverno/` |
| InSpec profiles | Compliance profiles for Docker, RHEL 9, and Ubuntu 22.04 | `hardening/inspec/` |
| ASVS L1 checks | OWASP ASVS L1 infra-layer Kyverno policies and Checkov checks | `hardening/asvs-l1-checks/` |
| Checkov checks | Essential Eight checks and supporting metadata | `hardening/essential-eight/` |
| Compliance mapping | Rule-to-framework mapping for catalog linking | `hardening/compliance-mapping.yaml` |

---

## Supported standards

| Standard | CLI value | Primary output |
|----------|-----------|----------------|
| CIS Kubernetes Benchmark v1.9 | `cis-k8s` | Kyverno policies |
| DISA STIG for Kubernetes | `stig-k8s` | Kyverno policies |
| NSA/CISA Kubernetes Hardening Guide | `nsa-k8s` | Kyverno policies + network policies |
| Pod Security Standards | `pod-security` | Kyverno policy |
| Container image signing | `image-signing` | Kyverno policy |
| OWASP ASVS L1 (infra layer) | `asvs-l1` | Kyverno policies + Checkov checks |
| CIS Docker Benchmark v1.6 | `cis-docker` | InSpec profile |
| CIS RHEL 9 Benchmark | `cis-rhel9` | InSpec profile |
| CIS Ubuntu 22.04 Benchmark | `cis-ubuntu22` | InSpec profile |
| Essential Eight | `essential-eight` | Checkov checks + README |

---

## Standard descriptions

### CIS Kubernetes Benchmark v1.9 (`cis-k8s`)

Published by the **Center for Internet Security (CIS)**, this benchmark provides prescriptive guidance for securing Kubernetes cluster components — API server, etcd, control-plane, kubelet, and RBAC. It is the most widely adopted baseline for Kubernetes hardening and is referenced by PCI-DSS, ISO 27001, and SOC 2 assessors. The generated Kyverno policies cover all five CIS sections (master node, etcd, control plane, worker nodes, and cluster policies).

### DISA STIG for Kubernetes (`stig-k8s`)

The **Defense Information Systems Agency (DISA) Security Technical Implementation Guide** for Kubernetes is mandatory for US Department of Defense (DoD) systems and systems hosted on FedRAMP-authorized cloud environments. It provides control identifiers (e.g., `V-242381`) that map directly into ATO (Authority to Operate) evidence packages. Use this standard if your workloads are subject to US federal compliance requirements.

### NSA/CISA Kubernetes Hardening Guide (`nsa-k8s`)

Jointly published by the **National Security Agency (NSA)** and the **Cybersecurity and Infrastructure Security Agency (CISA)**, this guide focuses on supply-chain risks, pod security, network segmentation, and audit logging. It is a recommended baseline for critical infrastructure operators. The generated artifacts include Kyverno pod-security policies and Kubernetes `NetworkPolicy` manifests for traffic segmentation.

### Pod Security Standards (`pod-security`)

A built-in Kubernetes standard that defines three profiles — **Privileged**, **Baseline**, and **Restricted** — governing what a pod is permitted to do at admission time. DevOps-OS generates a Kyverno `ClusterPolicy` that enforces the **Restricted** profile by default (no privilege escalation, no host namespaces, non-root containers, read-only root filesystems). Use this as a minimum baseline for any production cluster.

### Container Image Signing (`image-signing`)

Implements a **supply-chain integrity** control: every container image must be cryptographically signed with [Cosign](https://docs.sigstore.dev/cosign/overview/) before it is admitted to the cluster. The generated Kyverno policy verifies the Cosign signature against a public key at admission time, rejecting unsigned images. This aligns with SLSA Level 2+ and is required by several STIG controls.

### OWASP ASVS L1 — Infrastructure Layer (`asvs-l1`)

The **OWASP Application Security Verification Standard (ASVS) Level 1** defines baseline security requirements for web applications. The infra-layer subset enforced here covers:
- **V2** — Authentication: no default credentials in running containers
- **V6** — Stored cryptography: no plaintext secrets as environment variables
- **V8** — Data protection: TLS termination enforced at ingress
- **V9** — Communications: HTTP port 80 disallowed, TLS required on all ingresses
- **V14** — Configuration: containers run as non-root with least-privilege security contexts

This makes ASVS controls enforceable at the infrastructure admission layer, complementing application-level testing.

### CIS Docker Benchmark v1.6 (`cis-docker`)

Published by **CIS**, this benchmark audits the Docker host configuration, Docker daemon settings, Docker daemon files and permissions, container images, and container runtime configuration. The generated InSpec profile contains Ruby control files for each CIS section and is designed to be run with `inspec exec` against the Docker host. Applicable to any team running Docker or Podman as a container runtime.

### CIS RHEL 9 Benchmark (`cis-rhel9`)

Published by **CIS**, this benchmark covers hardening for **Red Hat Enterprise Linux 9** (and compatible distributions such as Rocky Linux and AlmaLinux). The generated InSpec profile audits filesystem configuration, inetd and special services, network parameters, logging and auditing, and access controls. Use this for any VM or bare-metal node running RHEL 9.

### CIS Ubuntu 22.04 Benchmark (`cis-ubuntu22`)

Published by **CIS**, this benchmark covers hardening for **Ubuntu 22.04 LTS**. The generated InSpec profile audits filesystem partitioning, software updates, network configuration, logging, user accounts, and file permissions. Ubuntu-specific control identifiers differ from the RHEL benchmark. Use this for Debian-family nodes including Ubuntu-based cloud VM images.

### Essential Eight (`essential-eight`)

Published by the **Australian Signals Directorate (ASD)**, the Essential Eight is mandatory for Australian government agencies and widely adopted by the private sector. It defines eight mitigation strategies across three maturity levels:
1. Application control
2. Patch applications
3. Configure Microsoft Office macro settings
4. User application hardening
5. Restrict administrative privileges
6. Patch operating systems
7. Multi-factor authentication
8. Regular backups

The generated Checkov checks enforce the infrastructure-applicable controls (items 1, 5, and 6) and the accompanying README explains maturity levels and which controls apply to containerised workloads.

---

## Which standard should I use?

Use this guide to choose the right baseline for your context. Standards can be combined — for example, a US DoD Kubernetes cluster may need both `stig-k8s` and `cis-rhel9`.

| Context | Recommended standards |
|---------|----------------------|
| Any production Kubernetes cluster (minimum baseline) | `cis-k8s`, `pod-security` |
| US DoD / FedRAMP / US federal systems | `stig-k8s`, `pod-security`, `image-signing` |
| Critical infrastructure (US) | `nsa-k8s`, `pod-security` |
| Australian Government / ASD mandate | `essential-eight`, `cis-k8s` |
| PCI-DSS scoped workloads | `cis-k8s`, `asvs-l1`, `pod-security` |
| HIPAA or ISO 27001 | `cis-k8s`, `asvs-l1`, `image-signing` |
| NIST 800-53 | `cis-k8s`, `stig-k8s`, `nsa-k8s` |
| Docker/container runtime compliance | `cis-docker` |
| RHEL 9 / Rocky / AlmaLinux OS nodes | `cis-rhel9` |
| Ubuntu 22.04 OS nodes | `cis-ubuntu22` |
| Supply-chain integrity enforcement | `image-signing` |
| Application-layer infrastructure controls | `asvs-l1` |
| Full production cluster hardening | `all` with `--compliance-framework` |

---

## Compliance framework to standard mapping

Use `--compliance-framework` to tag generated artifacts with control IDs for your target framework. The table below shows which hardening standards contribute controls to each framework.

| Compliance framework | Most relevant hardening standards |
|---------------------|----------------------------------|
| `pci-dss` | `cis-k8s`, `asvs-l1`, `pod-security`, `image-signing` |
| `hipaa` | `cis-k8s`, `asvs-l1`, `cis-rhel9`, `cis-ubuntu22` |
| `iso27001` | `cis-k8s`, `nsa-k8s`, `asvs-l1`, `essential-eight` |
| `nist-800-53` | `cis-k8s`, `stig-k8s`, `nsa-k8s`, `pod-security` |
| `soc2` | `cis-k8s`, `asvs-l1`, `image-signing`, `pod-security` |
| `rbi` | `cis-k8s`, `cis-docker`, `asvs-l1` |

---

## Quick start

```bash
# CIS Kubernetes guardrails
python -m cli.devopsos scaffold hardening --standard cis-k8s --type kyverno --environment production

# OWASP ASVS L1 infra-layer checks
python -m cli.devopsos scaffold hardening --standard asvs-l1

# Operating system baseline
python -m cli.devopsos scaffold hardening --standard cis-rhel9 --type inspec

# Full baseline set with compliance tagging
python -m cli.devopsos scaffold hardening --standard all --compliance-framework pci-dss
```

---

## Key options

| Option | Default | Description |
|--------|---------|-------------|
| `--standard` | `all` | Select a single baseline or generate all supported standards |
| `--type` | `all` | Limit output to `kyverno`, `inspec`, `checkov`, or generate all applicable artifacts |
| `--output` | `hardening` | Root directory for generated artifacts |
| `--compliance-framework` | _(none)_ | Add compliance control IDs for `pci-dss`, `hipaa`, `iso27001`, `rbi`, `nist-800-53`, or `soc2` |
| `--severity` | `medium` | Filter generated rules by minimum severity |
| `--environment` | `production` | Use `production` for `Enforce`; `dev` and `staging` generate `Audit` mode policies |

---

## Typical output layout

```text
hardening/
├── kyverno/
│   ├── cis-k8s/
│   ├── stig-k8s/
│   ├── nsa-k8s/
│   ├── pod-security-standards.yaml
│   └── image-signing.yaml
├── inspec/
│   ├── docker-cis/
│   ├── rhel9-cis/
│   └── ubuntu22-cis/
├── asvs-l1-checks/
│   ├── README.md
│   ├── kyverno/
│   └── checkov/
├── essential-eight/
└── compliance-mapping.yaml
```

---

## Validation examples

```bash
pytest tests/test_hardening_scaffold.py
kubectl apply --dry-run=client -f hardening/kyverno/
inspec check hardening/inspec/docker-cis/
python -c "import yaml; yaml.safe_load(open('hardening/compliance-mapping.yaml'))"
```

---

## compliance-mapping.yaml schema

The `compliance-mapping.yaml` file links each generated hardening rule to control IDs in one or more compliance frameworks. It is consumed by downstream tools (e.g., GovPilot) to build a compliance catalog.

**Top-level structure:**

```yaml
<standard>:             # e.g. cis-k8s, stig-k8s
  <rule_id>:            # e.g. cis-k8s-1.2.1
    title: "..."        # human-readable rule description
    severity: high      # critical | high | medium | low
    frameworks:
      pci-dss:          # framework key
        - "Req 2.2"     # list of matching control IDs
      nist-800-53:
        - "CM-6"
        - "SC-28"
```

**Example entry:**

```yaml
cis-k8s:
  cis-k8s-1.2.1:
    title: "Ensure that the --anonymous-auth argument is set to false"
    severity: high
    frameworks:
      pci-dss:
        - "Req 2.2"
        - "Req 8.2"
      nist-800-53:
        - "AC-3"
        - "IA-2"
      soc2:
        - "CC6.1"
```

The mapping is only generated when `--compliance-framework` is specified. Without that flag, `compliance-mapping.yaml` is still written but the `frameworks` block will be empty for each rule.

---

## Troubleshooting

### Kyverno not installed — dry-run fails

```
error: unable to recognize "hardening/kyverno/": no matches for kind "ClusterPolicy"
```

Install Kyverno first, then retry:

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
kubectl apply --dry-run=client -f hardening/kyverno/
```

### InSpec gem not found

```
bash: inspec: command not found
```

Install the InSpec binary gem:

```bash
gem install inspec-bin
inspec check hardening/inspec/docker-cis/
```

### image-signing policy requires Cosign v2+

The generated `image-signing.yaml` Kyverno policy uses the `imageVerification` rule which requires **Cosign v2** signatures. Signatures created with Cosign v1 will be rejected. Verify your Cosign version before signing images:

```bash
cosign version   # must be v2.0.0 or later
```

### Generated YAML silently overrides existing files

The `--output` directory is written unconditionally. If you have customised files in `hardening/`, move them to a different directory before re-running the scaffold command, or use a different `--output` path.

### `compliance-mapping.yaml` is empty

The frameworks block is only populated when `--compliance-framework` is provided. Run again with the flag:

```bash
python -m cli.devopsos scaffold hardening --standard all --compliance-framework pci-dss
```

---

For the full option table, environment variables, and examples, see the [CLI Reference]({{< relref "/docs/reference" >}}).
