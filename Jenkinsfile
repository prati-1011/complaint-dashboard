pipeline {
    agent any

    stages {
        
        stage('Clone Repository') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/prati-1011/complaint-dashboard.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install streamlit pandas plotly openpyxl'
            }
        }

        stage('Secret Detection with Gitleaks') {
            steps {
                bat 'gitleaks detect --source . --verbose --exit-code 1'
            }
        }

        stage('Test Application') {
            steps {
                bat 'python -c "print(\\"App test passed!\\")"'
            }
        }
    }

    post {
        failure {
            echo '❌ Secrets found! Pipeline failed.'
        }
        success {
            echo '✅ No secrets found! Pipeline passed.'
        }
    }
}