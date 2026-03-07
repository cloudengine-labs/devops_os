pipeline {
    agent {
        docker {
            image 'docker.io/yourorg/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    environment {
        WORKSPACE_DIR = '${WORKSPACE}'
        REGISTRY_URL = params.REGISTRY_URL ?: 'docker.io'
        IMAGE_NAME = params.IMAGE_NAME ?: 'devops-os-app'
        IMAGE_TAG = params.IMAGE_TAG ?: 'latest'
        PYTHON_ENABLED = params.PYTHON_ENABLED ?: true
        JAVA_ENABLED = params.JAVA_ENABLED ?: false
        JAVASCRIPT_ENABLED = params.JAVASCRIPT_ENABLED ?: true
        GO_ENABLED = params.GO_ENABLED ?: false
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
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm ci
                        npm run build --if-present
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
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ]; then
                        npm test || true
                    fi
                '''
                sh '''
                    if [ ${JAVASCRIPT_ENABLED} = 'true' ] && [ -f package.json ] && grep -q eslint package.json; then
                        npm run lint || true
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
            steps {
                script {
                    def imageName = "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}"
                    docker.withRegistry('https://' + REGISTRY_URL, 'registry-credentials') {
                        def customImage = docker.build(imageName)
                        customImage.push()
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