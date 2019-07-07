// withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'psql-db', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
//     sh("""echo uname=$USERNAME pwd=$PASSWORD""")
// }

pipeline {
    agent {
        docker {
            image 'jupyter/datascience-notebook'
            args '--user root:root'
            }
    }
    stages {
        stage('Username/Password') {
            environment {
                PSQL_CREDS = credentials("${psql-db}")
            }
            steps {
                sh("echo Username is $PSQL_CREDS_USR")
                sh("echo Password is $PSQL_CREDS_PSW")
            }
        }
        stage('Install..') {
            steps {
                script {
                    sh("""ls -la
                    python --version
                    pip install -r requirements.txt
                    """)
                }
            }
        }
        stage('RUN') {
            steps {
                script {
                    sh("""python3 macd/runner.py -u ${env.PSQL_CREDS_USR} -p ${env.PSQL_CREDS_PSW}""")
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