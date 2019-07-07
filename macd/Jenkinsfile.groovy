// node {
//     withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'psql-db', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
//         sh("""echo uname=$USERNAME pwd=$PASSWORD""")
//     }
// }
pipeline {
    agent {
        docker {
            image 'jupyter/datascience-notebook'
            args '--user root:root'
            }
    }
    withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'psql-db', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
        sh("""echo uname=$USERNAME pwd=$PASSWORD""")
    }
    stages {
        stage('Install..') {
            steps {
                script {
                    sh("""ls -la
                    python --version
                    pip install -r macd/requirements.txt
                    echo env.USERNAME
                    echo env.PASSWORD
                    """)
                }
            }
        }
        stage('RUN') {
            steps {
                script {
                    sh("""python3 macd/runner.py -u $USERNAME -p $PASSWORD""")
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