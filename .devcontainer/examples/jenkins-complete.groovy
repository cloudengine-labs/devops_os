pipeline {
    agent {
        docker {
            image 'docker.io/yourorg/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    parameters {
        booleanParam(name: 'PYTHON_ENABLED', defaultValue: true, description: 'Enable Python tools')
        booleanParam(name: 'JAVA_ENABLED', defaultValue: true, description: 'Enable Java tools')
        booleanParam(name: 'JAVASCRIPT_ENABLED', defaultValue: true, description: 'Enable Javascript tools')
        booleanParam(name: 'GO_ENABLED', defaultValue: true, description: 'Enable Go tools')
        booleanParam(name: 'KUBERNETES_DEPLOY', defaultValue: true, description: 'Deploy to Kubernetes')
        choice(name: 'K8S_METHOD', choices: ['kubectl', 'kustomize', 'argocd', 'flux'], defaultValue: 'kustomize', description: 'Kubernetes deployment method')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'test', 'staging', 'prod'], defaultValue: 'dev', description: 'Deployment environment')
        string(name: 'REGISTRY_URL', defaultValue: 'docker.io', description: 'Container registry URL')
        string(name: 'IMAGE_NAME', defaultValue: 'devops-os-app', description: 'Name of the container image')
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Container image tag')
    }
    environment {
        WORKSPACE_DIR = '${WORKSPACE}'
        REGISTRY_URL = params.REGISTRY_URL ?: 'docker.io'
        IMAGE_NAME = params.IMAGE_NAME ?: 'devops-os-app'
        IMAGE_TAG = params.IMAGE_TAG ?: 'latest'
        KUBERNETES_DEPLOY = params.KUBERNETES_DEPLOY ?: true
        K8S_METHOD = params.K8S_METHOD ?: 'kustomize'
        ENVIRONMENT = params.ENVIRONMENT ?: 'dev'
        PYTHON_ENABLED = params.PYTHON_ENABLED ?: true
        JAVA_ENABLED = params.JAVA_ENABLED ?: true
        JAVASCRIPT_ENABLED = params.JAVASCRIPT_ENABLED ?: true
        GO_ENABLED = params.GO_ENABLED ?: true
    }
    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        ansiColor('xterm')
    }
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f setup.py ]; then
                        pip install -e .
                    elif [ ${PYTHON_ENABLED} = 'true' ] && [ -f pyproject.toml ]; then
                        pip install -e .
                    fi
                '''
                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn -B package --file pom.xml
                    fi
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f build.gradle ]; then
                        ./gradlew build
                    fi
                '''
                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm ci
                        npm run build --if-present
                    fi
                '''
                sh '''
                    if [ ${GO_ENABLED} = 'true' ] && [ -f go.mod ]; then
                        go build -v ./...
                    fi
                '''
                archiveArtifacts artifacts: '**/target/*.jar, **/dist/*, **/build/*, **/*.zip, **/*.tar.gz', allowEmptyArchive: true
            }
        }
        stage('Test') {
            steps {
                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -f requirements.txt ]; then
                        pip install -r requirements.txt pytest pytest-cov
                    fi
                    if [ ${PYTHON_ENABLED} = 'true' ] && [ -d tests ]; then
                        python -m pytest --cov=./ --cov-report=xml
                    fi
                '''
                sh '''
                    if [ ${PYTHON_ENABLED} = 'true' ] && command -v pylint &> /dev/null; then
                        pylint --disable=C0111 **/*.py || true
                    fi
                '''
                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn -B test --file pom.xml
                    fi
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f build.gradle ]; then
                        ./gradlew test
                    fi
                '''
                sh '''
                    if [ ${JAVA_ENABLED} = 'true' ] && [ -f pom.xml ]; then
                        mvn checkstyle:checkstyle || true
                    fi
                '''
                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm test || true
                    fi
                '''
                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ] && grep -q eslint package.json; then
                        npm run lint || true
                    fi
                '''
                sh '''
                    if [ ${GO_ENABLED} = 'true' ] && [ -f go.mod ]; then
                        go test -v ./...
                    fi
                '''
                junit '**/target/surefire-reports/*.xml, **/test-results/*.xml, **/junit-reports/*.xml', allowEmptyResults: true
            }
        }
        stage('Deploy') {
            when {
                expression { 
                    return env.ENVIRONMENT != 'prod' || (env.ENVIRONMENT == 'prod' && currentBuild.resultIsBetterOrEqualTo('SUCCESS'))
                }
            }
            input {
                message "Deploy to production?"
                ok "Yes"
                submitter "admin"
                parameters {
                    string(name: 'CONFIRM_DEPLOY', defaultValue: 'no', description: 'Type YES to confirm deployment to production')
                }
                when {
                    expression { return env.ENVIRONMENT == 'prod' }
                }
            }
            steps {
                script {
                    def imageName = "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}"
                    docker.withRegistry('https://' + REGISTRY_URL, 'registry-credentials') {
                        def customImage = docker.build(imageName)
                        customImage.push()
                    }
                }
                script {
                    if (env.KUBERNETES_DEPLOY == 'true') {
                        // Set up Kubernetes credentials
                        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                            sh 'mkdir -p ~/.kube && cp $KUBECONFIG ~/.kube/config && chmod 600 ~/.kube/config'
                            
                            if (env.K8S_METHOD == 'kubectl') {
                                sh '''
                                    kubectl apply -f ./k8s/deployment.yaml
                                    kubectl apply -f ./k8s/service.yaml
                                    kubectl rollout status deployment/my-app
                                '''
                            } else if (env.K8S_METHOD == 'kustomize') {
                                sh '''
                                    kubectl apply -k ./k8s/overlays/${ENVIRONMENT}
                                    kubectl rollout status deployment/my-app
                                '''
                            } else if (env.K8S_METHOD == 'argocd') {
                                withCredentials([
                                    string(credentialsId: 'argocd-server', variable: 'ARGOCD_SERVER'),
                                    usernamePassword(credentialsId: 'argocd-credentials', usernameVariable: 'ARGOCD_USERNAME', passwordVariable: 'ARGOCD_PASSWORD')
                                ]) {
                                    sh '''
                                        argocd login $ARGOCD_SERVER --username $ARGOCD_USERNAME --password $ARGOCD_PASSWORD --insecure
                                        argocd app sync my-application
                                        argocd app wait my-application --health
                                    '''
                                }
                            } else if (env.K8S_METHOD == 'flux') {
                                sh '''
                                    flux reconcile source git flux-system
                                    flux reconcile kustomization flux-system
                                '''
                            }
                        }
                    }
                }
                sh '''
                    echo "Deployment completed successfully"
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}