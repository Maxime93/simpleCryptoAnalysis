pipeline {
    agent {
        docker {
            image 'jupyter/datascience-notebook'
            }
    }
    // agent any
    stages {
        stage('Install..') {
            steps {
                script {
                    sh("""pip3 install -r macd/requirements.txt""")
                }
            }
        }
        stage('RUN') {
            steps {
                script {
                    sh("""ls -la
                    python3 --version
                    python --version
                    python3 macd/runner.py""")
                }
            }
        }
    }
    post {
        always {
           step([$class: 'WsCleanup']) /* clean up our workspace */
        }
    }
}