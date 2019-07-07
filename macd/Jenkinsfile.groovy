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
            withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'psql-db', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
            sh("""echo uname=$USERNAME pwd=$PASSWORD""")
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