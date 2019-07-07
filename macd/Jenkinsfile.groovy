pipeline {
    agent {
        docker {
            image 'jupyter/datascience-notebook'
            args '--user root:root'
            }
    }
    stages {
        stage('Install..') {
            steps {
                script {
                    sh("""ls -la
                    apt-get update
                    apt-get install python3-pip libssl-dev libffi-dev libsasl2-modules libsasl2-dev libpq-dev jq -y
                    python --version
                    pip install stockstats==0.2.0
                    pip install psycopg2==2.8.3
                    """)
                }
            }
        }
        stage('RUN') {
            environment {
                PSQL_CREDS = credentials('psql_db_string')
            }
            steps {
                script {
                    sh("""python3 macd/runner.py -u $PSQL_CREDS_USR -p $PSQL_CREDS_PSW""")
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