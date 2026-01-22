pipeline {
    agent any

    environment {
        AWS_REGION   = "ap-southeast-1"
        FUNCTION_NAME = "vault-fun"
        LAYER_NAME    = "vault-layer"
    }

    stages {

        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/tina-snatak/lambda-test.git'
            }
        }

        stage('Prepare Tools') {
            steps {
                sh '''
                sudo apt-get update -y
                sudo apt-get install -y python3 python3-pip zip jq
                python3 --version
                python3 -m pip --version
                '''
            }
        }

        stage('Build Lambda Layer') {
            steps {
                sh '''
                rm -rf python layer.zip
                mkdir -p python

                # Ubuntu-safe pip install
                python3 -m pip install -r requirements.txt -t python/

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

                cat layer.json
                '''
            }
        }

        stage('Attach Layer to Lambda') {
            steps {
                sh '''
                LAYER_ARN=$(jq -r '.LayerVersionArn' layer.json)

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
                rm -f function.zip
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
