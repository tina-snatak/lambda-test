pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'ADD_LAYER',
            defaultValue: true,
            description: 'Do you want to build & attach Lambda Layer?'
        )
    }

    environment {
        AWS_REGION    = "ap-southeast-1"
        FUNCTION_NAME = "vault-fun"
        LAYER_NAME    = "vault-layer"
    }

    stages {

        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/tina-snatak/lambda-test.git'
            }
        }

        /* ================= OPTIONAL LAYER FLOW ================= */

        stage('Build Lambda Layer') {
            when {
                expression { params.ADD_LAYER }
            }
            steps {
                sh '''
                set -e
                rm -rf python layer.zip
                mkdir python
                python3 -m pip install -r requirements.txt -t python/
                cd python
                zip -r ../layer.zip .
                cd ..
                ls -lh layer.zip
                '''
            }
        }

        stage('Publish Lambda Layer') {
            when {
                expression { params.ADD_LAYER }
            }
            steps {
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds' 
                ]]) {
                    sh '''
                    aws lambda publish-layer-version \
                      --layer-name $LAYER_NAME \
                      --zip-file fileb://layer.zip \
                      --compatible-runtimes python3.10 \
                      --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Attach Layer to Lambda') {
            when {
                expression { params.ADD_LAYER }
            }
            steps {
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds' 
                ]]) {
                    sh '''
                    LAYER_ARN=$(aws lambda list-layer-versions \
                      --layer-name $LAYER_NAME \
                      --query 'LayerVersions[0].LayerVersionArn' \
                      --output text \
                      --region $AWS_REGION)

                    echo "Using Layer ARN: $LAYER_ARN"

                    aws lambda update-function-configuration \
                      --function-name $FUNCTION_NAME \
                      --layers $LAYER_ARN \
                      --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Wait for Lambda Update') {
            when {
                expression { params.ADD_LAYER }
            }
            steps {
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds' 
                ]]) {
                    sh '''
                    echo "⏳ Waiting for Lambda layer update to complete..."

                    for i in $(seq 1 30); do
                      STATUS=$(aws lambda get-function-configuration \
                        --function-name $FUNCTION_NAME \
                        --query 'LastUpdateStatus' \
                        --output text \
                        --region $AWS_REGION)

                      echo "Attempt $i → Status: $STATUS"

                      if [ "$STATUS" = "Successful" ]; then
                        echo "✅ Lambda update completed"
                        exit 0
                      fi

                      if [ "$STATUS" = "Failed" ]; then
                        echo "❌ Lambda update failed"
                        exit 1
                      fi

                      sleep 5
                    done

                    echo "❌ Timeout waiting for Lambda update"
                    exit 1
                    '''
                }
            }
        }

        /* ================= ALWAYS DEPLOY CODE ================= */

        stage('Package Lambda Function') {
            steps {
                sh 'zip -r function.zip lambda-function.py'
            }
        }

        stage('Deploy Lambda Code') {
            steps {
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds' 
                ]]) {
                    sh '''
                    aws lambda update-function-code \
                      --function-name $FUNCTION_NAME \
                      --zip-file fileb://function.zip \
                      --region $AWS_REGION
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ PIPELINE SUCCESS – Deployment completed"
        }
        failure {
            echo "❌ PIPELINE FAILED – check logs"
        }
    }
}
