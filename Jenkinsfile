pipeline {
    agent any

    environment {
        AWS_REGION    = "ap-southeast-1"
        FUNCTION_NAME = "vault-fun"
        LAYER_NAME    = "vault-layer"
    }

    stages {

        stage('Clone Repo') {
            steps {
                deleteDir()   // 💡 clean workspace (MOST IMPORTANT)
                git branch: 'main',
                    url: 'https://github.com/tina-snatak/lambda-test.git'
            }
        }

        stage('Build Lambda Layer') {
            steps {
                sh '''
                set -e

                echo "Cleaning old artifacts"
                rm -rf python layer.zip

                mkdir python

                echo "Installing dependencies"
                python3 -m pip install -r requirements.txt -t python/

                echo "Creating layer zip"
                cd python
                zip -r ../layer.zip .
                cd ..

                echo "Layer zip size:"
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

                    echo "Published layer:"
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
                    NEW_LAYER_ARN=$(jq -r '.LayerVersionArn' layer.json)

                    echo "New Layer ARN: $NEW_LAYER_ARN"

                    aws lambda update-function-configuration \
                      --function-name $FUNCTION_NAME \
                      --layers $NEW_LAYER_ARN \
                      --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Package Lambda Function') {
            steps {
                sh '''
                rm -f function.zip
                zip function.zip lambda_function.py
                ls -lh function.zip
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
            echo "✅ PIPELINE SUCCESS – Lambda deployed"
        }
        failure {
            echo "❌ PIPELINE FAILED – Check logs"
        }
    }
}
