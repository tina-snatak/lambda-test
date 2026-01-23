pipeline {
    agent any

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

        stage('Build Lambda Layer') {
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

        // 🔥 NEW WAIT STAGE (IMPORTANT)
        stage('Wait for Lambda Update') {
            steps {
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds' 
                ]]) {
                    sh '''
                    echo "⏳ Waiting for Lambda update to complete..."

                    for i in {1..12}; do
                      STATUS=$(aws lambda get-function-configuration \
                        --function-name $FUNCTION_NAME \
                        --query 'LastUpdateStatus' \
                        --output text \
                        --region $AWS_REGION)

                      echo "Current status: $STATUS"

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

        stage('Package Lambda Function') {
            steps {
                sh '''
                zip -r function.zip lambda-function.py
                '''
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
            echo "✅ PIPELINE SUCCESS – Lambda + Layer deployed"
        }
        failure {
            echo "❌ PIPELINE FAILED – check logs"
        }
    }
}
