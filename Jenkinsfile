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

                rm -rf python layer.zip venv
                mkdir python

                # create virtualenv (SAFE way)
                python3 -m venv venv
                . venv/bin/activate

                pip install -r requirements.txt -t python/

                deactivate
                rm -rf venv

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
                      --region $AWS_REGION > layer.json

                    cat layer.json
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
                    LAYER_ARN=$(jq -r '.LayerVersionArn' layer.json)

                    aws lambda update-function-configuration \
                      --function-name $FUNCTION_NAME \
                      --layers $LAYER_ARN \
                      --region $AWS_REGION
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
