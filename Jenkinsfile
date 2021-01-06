pipeline {
  agent any
  stages {
    stage('SonarQube LATEST analysis') {
      steps {
          withSonarQubeEnv('SQ Latest') {
            script {
              def scannerHome = tool 'SonarScanner';
              sh "${scannerHome}/bin/sonar-scanner"
            }
          }
      }
    }
    stage("SonarQube LATEST Quality Gate") {
      steps {
          timeout(time: 5, unit: 'MINUTES') {
            script {
              def qg = waitForQualityGate()
              if (qg.status != 'OK') {
                echo "Quality gate failed: ${qg.status}, proceeding anyway"
              }
            }
          }
      }
    }
  }
}