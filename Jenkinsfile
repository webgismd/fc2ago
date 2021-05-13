node('xxxx') {
    try{
        parameters {
            string(name: 'APPSERVER', defaultValue: 'jenkinsnodeexample')
            }

       

        withEnv(["GIT_SSL_NO_VERIFY=true",
                 "PYTHONPATH=E:\\sw_nt\\ArcGIS\\Pro2\\bin\\Python\\envs\\arcgispro-py3\\",
                 "APRX=fc2ago_wildfire.aprx",
                 "WGETHOME=E:\\sw_nt\\wget\\bin",
                 "WRKSPC=E:/sw_nt/jenkins/workspace/waops/fc2ago-wildfire/",
                 "FCSFILE=layers_for_ago2.txt"
				 ]) {

        stage ('SCM prepare'){
				deleteDir()
				checkout([$class: 'GitSCM', branches: [[name: '${gitTag}']], doGenerateSubmoduleConfigurations: false, extensions: [], gitTool: 'Default', submoduleCfg: [], userRemoteConfigs: [[credentialsId: '607141bd-ef34-4e80-8e7e-1134b7c77176', url: 'https://gogs.data.gov.bc.ca/waops/fc2ago.git']]])
				
		}

		stage("Copy Configs to the ${env.ENV} Server and run script to push data to ArcGIS Online") {
		          
              
                timeout(time: 15, unit: 'MINUTES') {
                     bat '''
                    set TEMP=%WORKSPACE%
                    set TMP=%TEMP%
                    
                    %PYTHONPATH%python.exe fc2ago-cron.py -pwd %agopassword% -path %WRKSPC%%APRX% -fcs %FCSFILE%
                '''
                }
            
               
        }
       } 
        
    } catch (e) {
        currentBuild.result = "FAILED"
        notifyFailed()
        throw e
    }
}

def notifyFailed() {
    emailext (
        subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
        body: """<html><body><p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
            <p>Check console output at "<a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>"</p></html></body>""",
        to: 'dataetl@gov.bc.ca datamaps@gov.bc.ca'
    )
}