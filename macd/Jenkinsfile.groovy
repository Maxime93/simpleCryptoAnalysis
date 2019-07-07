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
            environment {
                CREDS = credentials("${psql-db}")
            }
            steps {
                script {
                    sh("""echo ${env.CREDS_USR}
                    echo ${env.CREDS_PSW}
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