pipeline {
    agent any

    environment {
        AWS_REGION = "ap-southeast-1"
        FUNCTION_NAME = "vault-fun"
        LAYER_NAME = "vault-layer"
    }

    stages {

        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/tina-snatak/lambda-test.git'
            }
        }

        stage('Build Lambda Layer') {
            steps {
                sh '''
                rm -rf layer python layer.zip
                mkdir -p python
                pip3 install -r requirements.txt -t python/
                zip -r layer.zip python
                '''
            }
        }

        stage('Publish Lambda Layer') {
            steps {
                sh '''
                aws lambda publish-layer-version \
                  --layer-name $LAYER_NAME \
                  --zip-file fileb://layer.zip \
                  --compatible-runtimes python3.10 \
                  --region $AWS_REGION > layer.json
                '''
            }
        }

        stage('Attach Layer to Lambda') {
            steps {
                sh '''
                LAYER_ARN=$(cat layer.json | jq -r '.LayerVersionArn')

                aws lambda update-function-configuration \
                  --function-name $FUNCTION_NAME \
                  --layers $LAYER_ARN \
                  --region $AWS_REGION
                '''
            }
        }

        stage('Package Lambda Function') {
            steps {
                sh '''
                zip function.zip lambda_function.py
                '''
            }
        }

        stage('Deploy Lambda Code') {
            steps {
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
