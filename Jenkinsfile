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
                sh 'pyright . --lib'
            }
        }
        stage('Set dev version') {
            when {
                branch 'main'
            }
            steps {
                // This runs when we're not building a release or release candidate
                // It sets the version of the project to something containing the decimalised version of the
                // git commit id so that the package can be automatically deployed to testpypi.

                sh 'revision="$(git rev-parse HEAD | tr \'[:lower:]\' \'[:upper:]\')"; decimal_rev=$(echo "obase=10; ibase=16; $revision" | bc); poetry version "0.1.0-dev$decimal_rev"'
            }
        }
        stage('Package') {
            steps {
                sh 'poetry build'
                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
        stage('Publish to Test-pypi') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh "twine check dist/csvcubed_devtools*.whl"

                    withCredentials([usernamePassword(credentialsId: 'testpypi-robons', usernameVariable:'TWINE_USERNAME', passwordVariable: 'TWINE_PASSWORD')]) {
                        sh 'twine upload -r testpypi dist/csvcubed_devtools*.whl'
                    }
                }
            }
        }
        stage('Publish to Pypi') {
            when {
                buildingTag()
                tag pattern: "v\\d+\\.\\d+\\.\\d+(-RC\\d)?", comparator: "REGEXP"
            }
            steps {
                script {
                    sh "twine check dist/csvcubed_devtools*.whl"

                    withCredentials([usernamePassword(credentialsId: 'pypi-robons', usernameVariable:'TWINE_USERNAME', passwordVariable: 'TWINE_PASSWORD')]) {
                        sh 'twine upload dist/csvcubed_devtools*.whl'
                    }
                }
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
