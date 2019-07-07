pipeline {
    agent {
        docker {
            image 'jupyter/datascience-notebook'
            args '--user root:root'
            }
    }
    // agent any
    stages {
        stage('Install..') {
            steps {
                script {
                    sh("""ls -la
                    python --version
                    pip install -r macd/requirements.txt
                    """)
                }
            }
        }
        stage('RUN') {
            steps {
                script {
                    sh("""python3 macd/runner.py""")
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