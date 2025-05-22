# Base image with common tools
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Arguments for customization
ARG PYTHON_VERSION=3.11
ARG JAVA_VERSION=17
ARG NODE_VERSION=20
ARG GO_VERSION=1.21
ARG INSTALL_PYTHON=true
ARG INSTALL_JAVA=true 
ARG INSTALL_JS=true
ARG INSTALL_GO=true
ARG INSTALL_DOCKER=true
ARG INSTALL_TERRAFORM=true
ARG INSTALL_KUBECTL=true
ARG INSTALL_HELM=true
ARG INSTALL_GITHUB_ACTIONS=true

# Kubernetes tools
ARG INSTALL_K9S=true
ARG K9S_VERSION=0.29.1
ARG INSTALL_KUSTOMIZE=true
ARG KUSTOMIZE_VERSION=5.2.1
ARG INSTALL_ARGOCD_CLI=true
ARG ARGOCD_VERSION=2.8.4
ARG INSTALL_LENS=false
ARG INSTALL_KUBESEAL=true
ARG INSTALL_FLUX=true
ARG FLUX_VERSION=2.1.2
ARG INSTALL_KIND=true
ARG INSTALL_MINIKUBE=true
ARG INSTALL_OPENSHIFT_CLI=false

# Build tools
ARG INSTALL_GRADLE=true
ARG INSTALL_MAVEN=true
ARG INSTALL_ANT=true
ARG INSTALL_MAKE=true
ARG INSTALL_CMAKE=true

# Code analysis tools
ARG INSTALL_SONARQUBE=true
ARG INSTALL_CHECKSTYLE=true
ARG INSTALL_PMD=true
ARG INSTALL_ESLINT=true
ARG INSTALL_PYLINT=true

# DevOps tools
ARG INSTALL_NEXUS=true
ARG NEXUS_VERSION=3.50.0
ARG INSTALL_PROMETHEUS=true
ARG PROMETHEUS_VERSION=2.45.0
ARG INSTALL_GRAFANA=true
ARG GRAFANA_VERSION=10.0.0
ARG INSTALL_ELK=true
ARG INSTALL_JENKINS=false

# Essential build tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    wget \
    unzip \
    git \
    gnupg \
    lsb-release \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    jq

# Install Python if requested
RUN if [ "$INSTALL_PYTHON" = "true" ]; then \
    add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv python3-pip \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && python -m pip install --upgrade pip \
    && pip install pytest black flake8 mypy pipenv tox coverage pytest-cov; \
    fi

# Install Java if requested
RUN if [ "$INSTALL_JAVA" = "true" ]; then \
    apt-get update \
    && apt-get install -y openjdk-${JAVA_VERSION}-jdk maven gradle \
    && echo "export JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64" >> /etc/bash.bashrc; \
    fi

# Install Node.js/JavaScript if requested
RUN if [ "$INSTALL_JS" = "true" ]; then \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn typescript jest eslint prettier; \
    fi

# Install Go if requested
RUN if [ "$INSTALL_GO" = "true" ]; then \
    curl -OL https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz \
    && echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/bash.bashrc \
    && echo "export PATH=$PATH:/root/go/bin" >> /etc/bash.bashrc \
    && /usr/local/go/bin/go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest; \
    fi

# Install Docker if requested
RUN if [ "$INSTALL_DOCKER" = "true" ]; then \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; \
    fi

# Install Terraform if requested
RUN if [ "$INSTALL_TERRAFORM" = "true" ]; then \
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y terraform; \
    fi

# Install kubectl if requested
RUN if [ "$INSTALL_KUBECTL" = "true" ]; then \
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl; \
    fi

# Install Helm if requested
RUN if [ "$INSTALL_HELM" = "true" ]; then \
    curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" > /etc/apt/sources.list.d/helm-stable-debian.list \
    && apt-get update \
    && apt-get install -y helm; \
    fi

# Install K9s if requested
RUN if [ "$INSTALL_K9S" = "true" ]; then \
    mkdir -p /tmp/k9s && cd /tmp/k9s \
    && curl -sSLo k9s.tar.gz "https://github.com/derailed/k9s/releases/download/v${K9S_VERSION}/k9s_Linux_amd64.tar.gz" \
    && tar -xzf k9s.tar.gz \
    && chmod +x k9s \
    && mv k9s /usr/local/bin/ \
    && cd /tmp && rm -rf /tmp/k9s; \
    fi

# Install Kustomize if requested
RUN if [ "$INSTALL_KUSTOMIZE" = "true" ]; then \
    curl -sSLo /tmp/kustomize.tar.gz "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv${KUSTOMIZE_VERSION}/kustomize_v${KUSTOMIZE_VERSION}_linux_amd64.tar.gz" \
    && mkdir -p /tmp/kustomize \
    && tar -xzf /tmp/kustomize.tar.gz -C /tmp/kustomize \
    && chmod +x /tmp/kustomize/kustomize \
    && mv /tmp/kustomize/kustomize /usr/local/bin/ \
    && rm -rf /tmp/kustomize /tmp/kustomize.tar.gz; \
    fi

# Install ArgoCD CLI if requested
RUN if [ "$INSTALL_ARGOCD_CLI" = "true" ]; then \
    curl -sSLo /usr/local/bin/argocd "https://github.com/argoproj/argo-cd/releases/download/v${ARGOCD_VERSION}/argocd-linux-amd64" \
    && chmod +x /usr/local/bin/argocd; \
    fi

# Install Lens if requested
RUN if [ "$INSTALL_LENS" = "true" ]; then \
    apt-get update \
    && curl -fsSL https://downloads.k8slens.dev/keys/gpg | gpg --dearmor | tee /usr/share/keyrings/lens-archive-keyring.gpg > /dev/null \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/lens-archive-keyring.gpg] https://downloads.k8slens.dev/apt/debian stable main" | tee /etc/apt/sources.list.d/lens.list > /dev/null \
    && apt-get update \
    && apt-get install -y lens; \
    fi

# Install Kubeseal if requested
RUN if [ "$INSTALL_KUBESEAL" = "true" ]; then \
    wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.3/kubeseal-0.24.3-linux-amd64.tar.gz \
    && tar -xvzf kubeseal-0.24.3-linux-amd64.tar.gz kubeseal \
    && install -m 755 kubeseal /usr/local/bin/kubeseal \
    && rm kubeseal kubeseal-0.24.3-linux-amd64.tar.gz; \
    fi

# Install Flux if requested
RUN if [ "$INSTALL_FLUX" = "true" ]; then \
    curl -s https://fluxcd.io/install.sh | bash; \
    fi

# Install KinD if requested
RUN if [ "$INSTALL_KIND" = "true" ]; then \
    curl -Lo /usr/local/bin/kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-$(uname)-amd64" \
    && chmod +x /usr/local/bin/kind; \
    fi

# Install Minikube if requested
RUN if [ "$INSTALL_MINIKUBE" = "true" ]; then \
    curl -Lo /usr/local/bin/minikube "https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64" \
    && chmod +x /usr/local/bin/minikube; \
    fi

# Install OpenShift CLI if requested
RUN if [ "$INSTALL_OPENSHIFT_CLI" = "true" ]; then \
    curl -Lo /tmp/oc.tar.gz "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz" \
    && mkdir -p /tmp/oc \
    && tar -xzf /tmp/oc.tar.gz -C /tmp/oc \
    && chmod +x /tmp/oc/oc \
    && mv /tmp/oc/oc /usr/local/bin/ \
    && rm -rf /tmp/oc /tmp/oc.tar.gz; \
    fi

# Install GitHub Actions runner if requested
RUN if [ "$INSTALL_GITHUB_ACTIONS" = "true" ]; then \
    mkdir -p /opt/actions-runner \
    && cd /opt/actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v2.309.0/actions-runner-linux-x64-2.309.0.tar.gz \
    && tar xzf ./actions-runner-linux-x64-2.309.0.tar.gz \
    && rm actions-runner-linux-x64-2.309.0.tar.gz \
    && ./bin/installdependencies.sh; \
    fi

# Install Build Tools
# Make and CMake
RUN if [ "$INSTALL_MAKE" = "true" ] || [ "$INSTALL_CMAKE" = "true" ]; then \
    apt-get update \
    && apt-get install -y make; \
    fi

RUN if [ "$INSTALL_CMAKE" = "true" ]; then \
    apt-get update \
    && apt-get install -y cmake; \
    fi

# Ant (if not already installed with Java)
RUN if [ "$INSTALL_ANT" = "true" ]; then \
    apt-get update \
    && apt-get install -y ant; \
    fi

# Code Analysis Tools

# SonarQube Scanner
RUN if [ "$INSTALL_SONARQUBE" = "true" ]; then \
    mkdir -p /opt/sonar-scanner \
    && curl -sSLo /opt/sonar-scanner-cli.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip \
    && unzip /opt/sonar-scanner-cli.zip -d /opt \
    && mv /opt/sonar-scanner-* /opt/sonar-scanner \
    && rm /opt/sonar-scanner-cli.zip \
    && echo 'export PATH=$PATH:/opt/sonar-scanner/bin' >> /etc/bash.bashrc; \
    fi

# Checkstyle
RUN if [ "$INSTALL_CHECKSTYLE" = "true" ]; then \
    mkdir -p /opt/checkstyle \
    && curl -sSLo /opt/checkstyle/checkstyle.jar https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.12.0/checkstyle-10.12.0-all.jar \
    && echo '#!/bin/bash\njava -jar /opt/checkstyle/checkstyle.jar "$@"' > /usr/local/bin/checkstyle \
    && chmod +x /usr/local/bin/checkstyle; \
    fi

# PMD
RUN if [ "$INSTALL_PMD" = "true" ]; then \
    mkdir -p /opt/pmd \
    && curl -sSLo /opt/pmd.zip https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0-rc3/pmd-bin-7.0.0-rc3.zip \
    && unzip /opt/pmd.zip -d /opt \
    && mv /opt/pmd-bin-* /opt/pmd \
    && rm /opt/pmd.zip \
    && echo 'export PATH=$PATH:/opt/pmd/bin' >> /etc/bash.bashrc; \
    fi

# Install Pylint if not already installed with Python
RUN if [ "$INSTALL_PYLINT" = "true" ] && [ "$INSTALL_PYTHON" = "true" ]; then \
    pip install pylint; \
    fi

# Install ESLint if not already installed with Node.js
RUN if [ "$INSTALL_ESLINT" = "true" ] && [ "$INSTALL_JS" = "true" ]; then \
    npm install -g eslint; \
    fi

# DevOps Tools

# Sonatype Nexus
RUN if [ "$INSTALL_NEXUS" = "true" ]; then \
    mkdir -p /opt/nexus \
    && curl -sSLo /opt/nexus.tar.gz https://download.sonatype.com/nexus/3/nexus-${NEXUS_VERSION}-unix.tar.gz \
    && tar -xzf /opt/nexus.tar.gz -C /opt \
    && mv /opt/nexus-* /opt/nexus \
    && rm /opt/nexus.tar.gz \
    && echo '#!/bin/bash\n/opt/nexus/bin/nexus "$@"' > /usr/local/bin/nexus \
    && chmod +x /usr/local/bin/nexus \
    && echo 'export NEXUS_HOME=/opt/nexus' >> /etc/bash.bashrc; \
    fi

# Prometheus
RUN if [ "$INSTALL_PROMETHEUS" = "true" ]; then \
    mkdir -p /opt/prometheus \
    && curl -sSLo /opt/prometheus.tar.gz https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz \
    && tar -xzf /opt/prometheus.tar.gz -C /opt \
    && mv /opt/prometheus-* /opt/prometheus \
    && rm /opt/prometheus.tar.gz \
    && echo '#!/bin/bash\n/opt/prometheus/prometheus "$@"' > /usr/local/bin/prometheus \
    && chmod +x /usr/local/bin/prometheus; \
    fi

# Grafana
RUN if [ "$INSTALL_GRAFANA" = "true" ]; then \
    wget -q -O - https://packages.grafana.com/gpg.key | gpg --dearmor | tee /usr/share/keyrings/grafana.gpg > /dev/null \
    && echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list \
    && apt-get update \
    && apt-get install -y grafana; \
    fi

# ELK Stack (Elasticsearch, Logstash, Kibana)
RUN if [ "$INSTALL_ELK" = "true" ]; then \
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list \
    && apt-get update \
    && apt-get install -y elasticsearch kibana logstash; \
    fi

# Jenkins (optional)
RUN if [ "$INSTALL_JENKINS" = "true" ]; then \
    curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | tee \
    /usr/share/keyrings/jenkins-keyring.asc > /dev/null \
    && echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
    https://pkg.jenkins.io/debian-stable binary/ | tee \
    /etc/apt/sources.list.d/jenkins.list > /dev/null \
    && apt-get update \
    && apt-get install -y jenkins; \
    fi

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set the default shell to bash
ENV SHELL /bin/bash
