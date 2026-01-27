pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

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

        /* ================= CLEAN ================= */

        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        /* ================= CLONE REPO ================= */

        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/tina-snatak/lambda-test.git'
            }
        }

        /* ================= OPTIONAL LAYER FLOW ================= */

        stage('Build Lambda Layer') {
            when { expression { params.ADD_LAYER } }

            steps {
                sh '''
                set -e
                echo " Building Lambda Layer..."

                rm -rf python layer.zip
                mkdir python

                python3 -m pip install -r requirements.txt -t python/

                cd python
                zip -r ../layer.zip .
                cd ..

                echo " Layer Zip Created"
                ls -lh layer.zip
                '''
            }
        }

        stage('Publish Lambda Layer') {
            when { expression { params.ADD_LAYER } }

            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds'
                ]]) {
                    sh '''
                    echo " Publishing Lambda Layer..."

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
            when { expression { params.ADD_LAYER } }

            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds'
                ]]) {
                    sh '''
                    echo " Attaching Layer to Lambda..."

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

        /* ================= AWS BUILT-IN WAIT ================= */

        stage('Wait for Lambda Update') {
            when { expression { params.ADD_LAYER } }

            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds'
                ]]) {
                    sh '''
                    echo " Waiting for Lambda update to complete..."

                    aws lambda wait function-updated \
                      --function-name $FUNCTION_NAME \
                      --region $AWS_REGION

                    echo " Lambda update completed successfully"
                    '''
                }
            }
        }

        /* ================= ALWAYS DEPLOY CODE ================= */

        stage('Package Lambda Function') {
            steps {
                sh '''
                echo " Packaging Lambda Function..."
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
                    echo " Deploying Lambda Code..."

                    aws lambda update-function-code \
                      --function-name $FUNCTION_NAME \
                      --zip-file fileb://function.zip \
                      --region $AWS_REGION

                    echo "⏳ Waiting after code deployment..."

                    aws lambda wait function-updated \
                      --function-name $FUNCTION_NAME \
                      --region $AWS_REGION

                    echo " Lambda Code Deployment Completed"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo " PIPELINE SUCCESS – Deployment Completed"
        }
        failure {
            echo " PIPELINE FAILED – Check Logs"
        }
    }
}
