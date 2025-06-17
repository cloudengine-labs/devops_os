# Migration Plan: DevOps-OS Logical Grouping

This document tracks the movement of files for better logical grouping:

## .devcontainer/ (Dev Container Config)
- Dockerfile
- devcontainer.json
- devcontainer.env.json
- configure.py

## cicd/ (CI/CD Generators & Docs)
- generate-cicd.py
- github-actions-generator-improved.py
- jenkins-pipeline-generator-improved.py
- CI-CD-GENERATORS-USAGE.md
- CICD-GENERATORS-README.md
- CICD-TECH-STACK-README.md
- GITHUB-ACTIONS-README.md
- JENKINS-PIPELINE-README.md
- HowTo-Create-DevOps-Os-GHA-Jenkins.md

## kubernetes/ (Kubernetes Tools & Docs)
- k8s-config-generator.py
- KUBERNETES-DEPLOYMENT-README.md
- kubernetes-capabilities.md
- kubernetes-templates/

## docs/ (General Documentation)
- DEVOPS-OS-README.md
- DEVOPS-OS-QUICKSTART.md

## scripts/ (Examples, helper scripts)
- examples/

---

Update all references in documentation after moving files.
