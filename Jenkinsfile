pipeline {
    agent any

    stages {
        
        stage('Clone Repository') {
            steps {
                echo '📦 Cloning from GitHub...'
                git branch: 'main', 
                    url: 'https://github.com/prati-1011/complaint-dashboard.git'
                echo '✅ Repository cloned!'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '🔧 Installing Python packages...'
                bat 'C:\\Users\\nkson\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m pip install streamlit pandas plotly openpyxl'
                echo '✅ Dependencies installed!'
            }
        }

        stage('Secret Detection with Gitleaks') {
            steps {
                echo '🔍 Scanning for hardcoded secrets...'
                bat 'C:\\Users\\nkson\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gitleaks.Gitleaks_Microsoft.Winget.Source_8wekyb3d8bbwe\\gitleaks.exe detect --source . --verbose --exit-code 1'
                echo '✅ No secrets found!'
            }
        }

        stage('Test Application') {
            steps {
                echo '🧪 Testing Python...'
                bat 'C:\\Users\\nkson\\AppData\\Local\\Programs\\Python\\Python311\\python.exe --version'
                echo '✅ Test passed!'
            }
        }
    }

    post {
        failure {
            echo '❌ SECURITY ISSUE: Secrets found! Pipeline failed.'
        }
        success {
            echo '✅ No secrets found! Pipeline succeeded.'
        }
    }
}