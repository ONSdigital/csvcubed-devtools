pipeline {
    agent {
        dockerfile {
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }
    stages {
        stage('Pyright') {
            steps {
                sh 'poetry run pyright . --lib'
            }
        }
        stage('Package') {
            steps {
                sh 'poetry build'
                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
    }
    post {
        always {
            script {
                try {
                    unstash name: 'wheels'
                } catch (Exception e) {
                    echo 'wheels stash does not exist'
                }

                archiveArtifacts artifacts: '**/dist/*.whl', fingerprint: true

                // Set more permissive permissions on all files so future processes/Jenkins can easily delete them.
                sh 'chmod -R ugo+rw .'
                // Clean up any unwanted files lying about.
                sh "git clean -fxd --exclude='.venv'"
            }
        }
    }
}
