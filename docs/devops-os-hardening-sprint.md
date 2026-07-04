# DevOps-OS Hardening Sprint

## 1. Sprint Goal

The `devopsos scaffold hardening` command delivers production-ready infrastructure hardening configurations — Kyverno ClusterPolicies, InSpec compliance profiles, and Checkov custom checks — generated directly from the DevOps-OS CLI. It belongs in devops_os (not GovPilot) because it is a general-purpose scaffold generator that produces standard-compliant YAML and Ruby artifacts consumable by any Kubernetes cluster, container runtime, or operating system; GovPilot is the downstream consumer that ingests these artifacts via its `check_selector.py` compliance catalog linker. By centralising hardening scaffold generation in devops_os, any team can bootstrap a compliant posture in seconds, while GovPilot retains responsibility for gap-register tracking and evidence collection.

---

## 2. Hardening Standards Covered

| Standard | Target | Tool | Files Generated |
|---|---|---|---|
| CIS Kubernetes Benchmark v1.9 | Kubernetes cluster | Kyverno YAML policies | `kyverno/cis-k8s/1-master-node-config.yaml` … `5-policies.yaml` |
| CIS Docker Benchmark v1.6 | Container runtime | InSpec profile | `inspec/docker-cis/` |
| CIS RHEL 9 Benchmark | OS (RHEL/Rocky/AlmaLinux) | InSpec profile | `inspec/rhel9-cis/` |
| CIS Ubuntu 22.04 Benchmark | OS (Ubuntu) | InSpec profile | `inspec/ubuntu22-cis/` |
| DISA STIG for Kubernetes | Kubernetes cluster | Kyverno YAML policies | `kyverno/stig-k8s/stig-cluster-policies.yaml` |
| NSA/CISA Kubernetes Hardening Guide | Kubernetes cluster | Kyverno + NetworkPolicy | `kyverno/nsa-k8s/pod-security.yaml`, `network-policies.yaml` |
| Pod Security Standards (Kubernetes) | Pod admission | Kyverno ClusterPolicy | `kyverno/pod-security-standards.yaml` |
| Container Image Signing | CI/CD + admission | Kyverno + Cosign policy | `kyverno/image-signing.yaml` |
| Essential Eight (Australia ASD) | General controls | Checkov | `essential-eight/` |

---

## 3. CLI Design

```bash
# Generate CIS Kubernetes hardening policies
devopsos scaffold hardening --standard cis-k8s --output hardening/

# Generate DISA STIG Kubernetes policies
devopsos scaffold hardening --standard stig-k8s --output hardening/

# Generate OS hardening InSpec profile for RHEL 9
devopsos scaffold hardening --standard cis-rhel9 --type inspec --output hardening/

# Generate all Kyverno policies for a production cluster
devopsos scaffold hardening --standard all --type kyverno --output hardening/

# Generate with compliance mapping (links back to GovPilot gap register)
devopsos scaffold hardening --standard cis-k8s --compliance-framework pci-dss --output hardening/
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--standard` | Hardening standard: `cis-k8s`, `stig-k8s`, `nsa-k8s`, `cis-docker`, `cis-rhel9`, `cis-ubuntu22`, `pod-security`, `image-signing`, `essential-eight`, `all` | `all` |
| `--type` | Output type: `kyverno`, `inspec`, `checkov`, `all` | `all` applicable |
| `--output` | Output directory | `./hardening/` |
| `--compliance-framework` | Tag outputs with compliance framework IDs (`pci-dss`, `hipaa`, `iso27001`, `rbi`, `nist-800-53`, `soc2`) for GovPilot catalog linking | _(none)_ |
| `--severity` | Filter by minimum severity level: `critical`, `high`, `medium`, `low` | `medium` |
| `--environment` | Target environment profile: `dev`, `staging`, `production` (adjusts Kyverno `validationFailureAction`) | `production` |

---

## 4. File Structure Generated

```
hardening/
├── kyverno/
│   ├── cis-k8s/
│   │   ├── 1-master-node-config.yaml       — CIS 1.x master node API server settings
│   │   ├── 2-etcd-config.yaml              — CIS 2.x etcd security
│   │   ├── 3-control-plane-config.yaml     — CIS 3.x control plane settings
│   │   ├── 4-worker-node-config.yaml       — CIS 4.x kubelet settings
│   │   └── 5-policies.yaml                 — CIS 5.x policies (RBAC, secrets, networking)
│   ├── stig-k8s/
│   │   └── stig-cluster-policies.yaml      — DISA STIG rules for K8s
│   ├── nsa-k8s/
│   │   ├── pod-security.yaml               — NSA pod hardening
│   │   └── network-policies.yaml           — NSA network segmentation
│   ├── pod-security-standards.yaml         — Baseline/Restricted PSS enforcement
│   └── image-signing.yaml                  — Cosign image signature verification
├── inspec/
│   ├── docker-cis/
│   │   ├── inspec.yml                      — profile metadata
│   │   └── controls/
│   │       ├── 1_host_configuration.rb     — CIS 1.x host config checks
│   │       ├── 2_docker_daemon.rb          — CIS 2.x daemon config
│   │       ├── 3_docker_daemon_files.rb    — CIS 3.x file permissions
│   │       ├── 4_container_images.rb       — CIS 4.x image checks
│   │       └── 5_container_runtime.rb      — CIS 5.x runtime config
│   ├── rhel9-cis/
│   │   ├── inspec.yml
│   │   └── controls/
│   │       ├── 1_filesystem.rb             — CIS 1.x filesystem config
│   │       ├── 2_services.rb               — CIS 2.x inetd, special services
│   │       ├── 3_network.rb                — CIS 3.x network params
│   │       ├── 4_logging.rb                — CIS 4.x logging and auditing
│   │       └── 5_access.rb                 — CIS 5.x access, auth, sudo
│   └── ubuntu22-cis/
│       ├── inspec.yml
│       └── controls/ (same structure as rhel9-cis)
├── essential-eight/
│   ├── README.md                           — maturity levels and applicability
│   └── checkov/
│       └── essential-eight-checks.py       — Checkov custom checks for E8
└── compliance-mapping.yaml                 — maps each hardening rule → compliance control IDs
                                              (used by GovPilot check catalog)
```

---

## 5. Implementation Plan

### Task 1 — CLI scaffold module (`cli/scaffold_hardening.py`)

- Typer sub-app with all options (`--standard`, `--type`, `--output`, `--compliance-framework`, `--severity`, `--environment`)
- Dispatcher calls template generators per standard
- `_enforcement_action()` helper maps `--environment` → Kyverno `validationFailureAction` (`Enforce` for production, `Audit` for dev/staging)
- Registered in `cli/devopsos.py` as `scaffold_app.command("hardening")`
- ~600 lines

### Task 2 — Kyverno policy templates (`hardening/templates/kyverno/`)

- YAML templates for each standard (CIS K8s sections 1–5, STIG, NSA, pod security, image signing)
- Each policy `metadata.annotations` carries:
  - `policies.kyverno.io/category` — standard name
  - `policies.kyverno.io/severity` — severity level
  - `devops-os/compliance` — comma-separated `standard:control-id` pairs for GovPilot catalog linking
- `validationFailureAction` parameterised via `--environment`

### Task 3 — InSpec profile templates (`hardening/templates/inspec/`)

- Skeleton InSpec profiles for Docker CIS, RHEL9 CIS, Ubuntu 22 CIS
- Each profile includes:
  - `inspec.yml` with profile metadata (name, title, maintainer, version, platform support)
  - `controls/*.rb` — Ruby control files referencing CIS benchmark section + compliance IDs via `tag compliance:`
- Controls structured as `control "cis-<os>-<section>.<number>" do … end`

### Task 4 — Compliance mapping file (`hardening/templates/compliance-mapping.yaml`)

- YAML file linking each hardening rule to compliance framework control IDs
- Format: `standard → rule_id → { title, framework: [control_ids] }`
- Consumed by GovPilot `check_selector.py` to link hardening checks into the catalog

---

## 6. Dependencies

| Tool | Purpose | Installation |
|------|---------|-------------|
| [Kyverno](https://kyverno.io) | Kubernetes admission control policy engine | `helm install kyverno kyverno/kyverno` |
| [InSpec](https://docs.chef.io/inspec/) | Compliance-as-code audit framework | `gem install inspec-bin` |
| [Cosign](https://docs.sigstore.dev/cosign/overview/) | Container image signing/verification | `brew install cosign` |
| [Checkov](https://www.checkov.io) | IaC static analysis + custom checks | `pip install checkov` |

---

## 7. Testing Plan

| Test | Scope | Command |
|------|-------|---------|
| Unit tests for scaffold generator | Python | `pytest tests/test_hardening_scaffold.py` |
| Validate generated Kyverno YAML | Dry-run | `kubectl apply --dry-run=client -f hardening/kyverno/` |
| Validate InSpec profiles | Profile check | `inspec check hardening/inspec/docker-cis/` |
| Verify compliance mapping YAML | Schema check | `python -c "import yaml; yaml.safe_load(open('hardening/compliance-mapping.yaml'))"` |
| End-to-end scaffold generation | Integration | `python -m cli.devopsos scaffold hardening --standard all --output /tmp/hardening-test` |

---

## 8. Effort Estimate

| Task | Description | Estimated Days | Team |
|------|-------------|---------------|------|
| Task 1 | CLI scaffold module (`cli/scaffold_hardening.py`) | 1.5 | devops-os team |
| Task 2 | Kyverno policy templates (5 standards × avg 2 files) | 2.0 | devops-os team |
| Task 3 | InSpec profile templates (3 OS × 5 controls) | 2.0 | devops-os team |
| Task 4 | Compliance mapping YAML + GovPilot integration hook | 1.0 | cel-agents team |
| Testing | Unit tests, dry-run validation, integration tests | 1.0 | devops-os team |
| Docs | Sprint doc, CLI reference update | 0.5 | devops-os team |
| **Total** | | **8.0** | |
