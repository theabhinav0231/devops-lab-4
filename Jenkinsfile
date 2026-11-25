pipeline {
    agent any
    environment {
        APP_NAME = 'devops-lab4-app'
        PYTHONPATH = '.'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }
        stage('Unit Tests (Gate 1)') {
            steps {
                sh 'python3 -m pytest tests/test_unit.py -v --junitxml=reports/junit-unit.xml'
            }
        }
        stage('Integration Tests (Gate 2)') {
            steps {
                sh 'python3 -m pytest tests/test_integration.py -v --junitxml=reports/junit-integration.xml'
            }
        }
        stage('Build Container Image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=4.1.0 -t devops-lab4-app:4.1.0 .'
            }
        }
        stage('Deploy (Gated)') {
            steps {
                sh 'echo "All automated test gates passed; image devops-lab4-app:4.1.0 promoted for deployment."'
            }
        }
    }
    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit-*.xml'
        }
        failure {
            echo 'PIPELINE GATE BLOCKED: Automated tests failed; deployment aborted.'
        }
    }
}
