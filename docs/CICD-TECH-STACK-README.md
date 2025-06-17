# Implementing CI/CD Pipelines for Technology Stacks

This guide provides specific instructions for implementing CI/CD pipelines for common technology stacks using the DevOps-OS tooling. Each technology stack has unique requirements and best practices that are supported by the DevOps-OS generators.

## Table of Contents

- [General Approach](#general-approach)
- [Python Applications](#python-applications)
- [Java Applications](#java-applications)
- [JavaScript/Node.js Applications](#javascriptnode-js-applications)
- [Go Applications](#go-applications)
- [Multi-language Microservices](#multi-language-microservices)
- [Containerized Applications](#containerized-applications)
- [Serverless Applications](#serverless-applications)
- [Database Migrations](#database-migrations)
- [Integration with External Services](#integration-with-external-services)
- [Custom Extensions](#custom-extensions)

## General Approach

For any technology stack, follow these general steps:

1. **Identify the stack requirements**: Build tools, testing frameworks, deployment targets, etc.
2. **Configure DevOps-OS container**: Edit `devcontainer.env.json` to enable the required languages and tools.
3. **Generate CI/CD configurations**: Use the appropriate generator for your CI/CD platform.
4. **Customize for your stack**: Edit the generated configurations or provide custom values.
5. **Deploy and test**: Push your changes and verify the CI/CD pipeline works.

## Python Applications

### Web Frameworks (Flask, Django, FastAPI)

```bash
# Generate CI/CD for Python web application
python generate-cicd.py --languages python --name "Python Web" --custom-values python-web-config.json
```

Example `python-web-config.json`:
```json
{
  "build": {
    "pip_requirements": "requirements.txt",
    "install_dev_dependencies": true
  },
  "test": {
    "framework": "pytest",
    "coverage": true,
    "linting": ["flake8", "pylint"],
    "type_checking": "mypy"
  },
  "deploy": {
    "wsgi_server": "gunicorn",
    "static_files": true,
    "environment_variables": ["DATABASE_URL", "SECRET_KEY"]
  }
}
```

### Data Science (Jupyter, pandas, scikit-learn)

```bash
# Generate CI/CD for Python data science project
python generate-cicd.py --languages python --name "Data Science" --custom-values data-science-config.json
```

Example `data-science-config.json`:
```json
{
  "build": {
    "pip_requirements": "requirements.txt",
    "conda_environment": "environment.yml"
  },
  "test": {
    "framework": "pytest",
    "notebook_testing": true
  },
  "deploy": {
    "model_serialization": "pickle",
    "model_registry": "mlflow",
    "environment_variables": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  }
}
```

## Java Applications

### Spring Boot Applications

```bash
# Generate CI/CD for Spring Boot application
python generate-cicd.py --languages java --name "Spring Boot" --custom-values spring-boot-config.json
```

Example `spring-boot-config.json`:
```json
{
  "build": {
    "build_tool": "maven",
    "java_version": "17",
    "maven_goals": ["clean", "package", "spring-boot:build-image"],
    "dependencies": ["spring-boot-starter-web", "spring-boot-starter-data-jpa"]
  },
  "test": {
    "frameworks": ["junit", "mockito"],
    "integration_tests": true,
    "code_quality": ["checkstyle", "pmd", "spotbugs"]
  },
  "deploy": {
    "platform": "kubernetes",
    "health_check_path": "/actuator/health",
    "environment_variables": ["SPRING_PROFILES_ACTIVE", "DATABASE_URL"]
  }
}
```

### Jakarta EE Applications

```bash
# Generate CI/CD for Jakarta EE application
python generate-cicd.py --languages java --name "Jakarta EE" --custom-values jakarta-ee-config.json
```

Example `jakarta-ee-config.json`:
```json
{
  "build": {
    "build_tool": "maven",
    "java_version": "17",
    "maven_goals": ["clean", "package"],
    "packaging": "war",
    "server": "wildfly"
  },
  "test": {
    "frameworks": ["junit", "arquillian"],
    "integration_tests": true
  },
  "deploy": {
    "application_server": "wildfly",
    "datasource": "java:jboss/datasources/ExampleDS",
    "environment_variables": ["JNDI_NAME", "RESOURCE_DIR"]
  }
}
```

## JavaScript/Node.js Applications

### React/Vue/Angular Frontend

```bash
# Generate CI/CD for JavaScript frontend application
python generate-cicd.py --languages javascript --name "Frontend" --custom-values frontend-config.json
```

Example `frontend-config.json`:
```json
{
  "build": {
    "package_manager": "npm",
    "build_command": "npm run build",
    "environment": "node",
    "node_version": "18"
  },
  "test": {
    "framework": "jest",
    "linting": "eslint",
    "e2e": "cypress"
  },
  "deploy": {
    "static_hosting": true,
    "cdn": "cloudfront",
    "environment_variables": ["API_URL", "ANALYTICS_ID"]
  }
}
```

### Node.js Backend

```bash
# Generate CI/CD for Node.js backend application
python generate-cicd.py --languages javascript --name "Node Backend" --custom-values node-backend-config.json
```

Example `node-backend-config.json`:
```json
{
  "build": {
    "package_manager": "npm",
    "build_command": "npm run build",
    "environment": "node",
    "node_version": "18",
    "typescript": true
  },
  "test": {
    "framework": "mocha",
    "linting": "eslint",
    "code_coverage": "istanbul"
  },
  "deploy": {
    "platform": "kubernetes",
    "health_check_path": "/health",
    "environment_variables": ["DATABASE_URL", "JWT_SECRET"]
  }
}
```

## Go Applications

### Go API Services

```bash
# Generate CI/CD for Go API application
python generate-cicd.py --languages go --name "Go API" --custom-values go-api-config.json
```

Example `go-api-config.json`:
```json
{
  "build": {
    "go_version": "1.21",
    "build_command": "go build -o api ./cmd/api",
    "dependencies": "go mod download"
  },
  "test": {
    "test_command": "go test -v -race -coverprofile=coverage.out ./...",
    "linting": "golangci-lint",
    "benchmarking": true
  },
  "deploy": {
    "platform": "kubernetes",
    "binary_name": "api",
    "environment_variables": ["DATABASE_DSN", "API_KEY"]
  }
}
```

### Go CLI Applications

```bash
# Generate CI/CD for Go CLI application
python generate-cicd.py --languages go --name "Go CLI" --custom-values go-cli-config.json
```

Example `go-cli-config.json`:
```json
{
  "build": {
    "go_version": "1.21",
    "build_command": "go build -o cli ./cmd/cli",
    "cross_compile": {
      "os": ["linux", "darwin", "windows"],
      "arch": ["amd64", "arm64"]
    }
  },
  "test": {
    "test_command": "go test -v ./...",
    "linting": "golangci-lint"
  },
  "deploy": {
    "platform": "github-release",
    "artifacts": ["cli", "cli.exe", "cli-darwin-amd64", "cli-linux-amd64"],
    "environment_variables": ["GITHUB_TOKEN"]
  }
}
```

## Multi-language Microservices

For microservices applications with multiple languages:

```bash
# Generate CI/CD for microservices application
python generate-cicd.py --languages python,java,javascript,go --name "Microservices" --kubernetes --k8s-method kustomize --custom-values microservices-config.json
```

Example `microservices-config.json`:
```json
{
  "services": [
    {
      "name": "api-gateway",
      "language": "java",
      "build_tool": "maven",
      "port": 8080,
      "dependencies": ["auth-service", "user-service"]
    },
    {
      "name": "auth-service",
      "language": "python",
      "requirements": "requirements.txt",
      "port": 5000
    },
    {
      "name": "user-service",
      "language": "javascript",
      "package_manager": "npm",
      "port": 3000
    },
    {
      "name": "metrics-service",
      "language": "go",
      "port": 4000
    }
  ],
  "common": {
    "container_registry": "docker.io/myorg",
    "kubernetes_namespace": "microservices",
    "environment_variables": ["SERVICE_MESH_ENABLED", "LOG_LEVEL"]
  }
}
```

## Containerized Applications

For applications that are already containerized:

```bash
# Generate CI/CD for containerized application
python generate-cicd.py --kubernetes --k8s-method kubectl --name "Containerized App" --custom-values container-config.json
```

Example `container-config.json`:
```json
{
  "docker": {
    "dockerfile": "Dockerfile",
    "context": ".",
    "image_name": "myapp",
    "tags": ["latest", "${GITHUB_SHA:0:7}"],
    "build_args": {
      "BUILD_ENV": "production"
    }
  },
  "registry": {
    "url": "docker.io/myorg",
    "credentials": "docker-registry-credentials"
  },
  "kubernetes": {
    "namespace": "apps",
    "deployment_name": "myapp",
    "resources": {
      "cpu": "500m",
      "memory": "512Mi"
    },
    "environment_variables": ["DATABASE_URL", "REDIS_HOST"]
  }
}
```

## Serverless Applications

For serverless applications:

```bash
# Generate CI/CD for serverless application
python generate-cicd.py --name "Serverless" --custom-values serverless-config.json
```

Example `serverless-config.json`:
```json
{
  "serverless": {
    "framework": "aws-lambda",
    "runtime": "nodejs18.x",
    "functions": ["api", "worker", "scheduler"],
    "deployment_tool": "serverless-framework"
  },
  "build": {
    "language": "javascript",
    "package_manager": "npm",
    "build_command": "npm run build"
  },
  "test": {
    "framework": "jest",
    "environment": "node"
  },
  "deploy": {
    "stage": "${ENV:-dev}",
    "region": "us-east-1",
    "environment_variables": ["DATABASE_URL", "AWS_REGION"]
  }
}
```

## Database Migrations

For applications with database migrations:

```bash
# Generate CI/CD with database migration support
python generate-cicd.py --name "App with DB" --custom-values db-migration-config.json
```

Example `db-migration-config.json`:
```json
{
  "database": {
    "type": "postgresql",
    "migration_tool": "flyway",
    "migration_location": "db/migrations",
    "test_database": {
      "enabled": true,
      "container": "postgres:13"
    }
  },
  "build": {
    "language": "java",
    "build_tool": "maven"
  },
  "deploy": {
    "migration_job": {
      "enabled": true,
      "pre_deployment": true,
      "timeout": 300
    },
    "environment_variables": ["DB_URL", "DB_USER", "DB_PASSWORD"]
  }
}
```

## Integration with External Services

### Integrating with SonarQube

```bash
# Generate CI/CD with SonarQube integration
python generate-cicd.py --name "Sonar Integration" --custom-values sonar-config.json
```

Example `sonar-config.json`:
```json
{
  "sonarqube": {
    "enabled": true,
    "server": "https://sonar.example.com",
    "project_key": "my-project",
    "credentials": "sonar-token",
    "quality_gate": {
      "enabled": true,
      "fail_on_error": true
    }
  },
  "build": {
    "language": "java",
    "build_tool": "maven",
    "sonar_plugin": true
  }
}
```

### Integrating with Artifactory

```bash
# Generate CI/CD with Artifactory integration
python generate-cicd.py --name "Artifactory Integration" --custom-values artifactory-config.json
```

Example `artifactory-config.json`:
```json
{
  "artifactory": {
    "enabled": true,
    "server": "https://artifactory.example.com",
    "repository": "my-repo",
    "credentials": "artifactory-credentials",
    "publish": {
      "artifacts": ["jar", "war", "docker"]
    }
  },
  "build": {
    "language": "java",
    "build_tool": "maven"
  }
}
```

## Custom Extensions

You can extend the CI/CD generators with custom stages:

```bash
# Generate CI/CD with custom stages
python generate-cicd.py --name "Custom Pipeline" --custom-values custom-stages-config.json
```

Example `custom-stages-config.json`:
```json
{
  "custom_stages": [
    {
      "name": "security-scan",
      "after": "test",
      "steps": [
        "echo 'Running security scan'",
        "trivy image ${IMAGE_NAME}:${IMAGE_TAG}",
        "snyk test"
      ]
    },
    {
      "name": "performance-test",
      "after": "security-scan",
      "steps": [
        "echo 'Running performance tests'",
        "k6 run performance-tests.js"
      ],
      "condition": "${ENV} == 'staging'"
    }
  ],
  "build": {
    "language": "javascript",
    "package_manager": "npm"
  }
}
```

## CI/CD Pipeline Templates by Technology Stack

Below are example commands to generate CI/CD pipelines for specific technology stacks:

### Python Flask Application

```bash
python github-actions-generator-improved.py --name "Flask API" --languages python --type complete --custom-values flask-config.json
```

### Spring Boot Java Application

```bash
python github-actions-generator-improved.py --name "Spring Boot" --languages java --type complete --kubernetes --k8s-method kustomize --custom-values spring-config.json
```

### React Frontend Application

```bash
python github-actions-generator-improved.py --name "React App" --languages javascript --type complete --custom-values react-config.json
```

### Go Microservice

```bash
python github-actions-generator-improved.py --name "Go Microservice" --languages go --type complete --kubernetes --custom-values go-microservice-config.json
```

### Full-Stack JavaScript Application

```bash
python jenkins-pipeline-generator-improved.py --name "MERN Stack" --languages javascript --type complete --parameters --custom-values mern-stack-config.json
```

### Multi-Service Platform

```bash
python github-actions-generator-improved.py --name "Platform" --languages python,java,javascript,go --type complete --kubernetes --k8s-method argocd --matrix --custom-values platform-config.json
```

## Next Steps

- Learn about [Creating DevOps-OS Using Dev Container](./DEVOPS-OS-README.md)
- Learn about [Creating Customized GitHub Actions Templates](./GITHUB-ACTIONS-README.md)
- Learn about [Creating Customized Jenkins Pipeline Templates](./JENKINS-PIPELINE-README.md)
- Explore [Creating Kubernetes Deployments](./KUBERNETES-DEPLOYMENT-README.md)
