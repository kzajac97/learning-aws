# Serverless

This application is example IoT processing application using AWS Lambda, DynamoDB and Step-Functions. The application
has number of features and is deployed using terragrunt with parameterized configuration.

### Components

1. Sensor Lambda - function is an example of IoT ingest from remote sensor, doing simple calculation
2. SQS - communication layer between sensor and analytics module
3. Analytics - step-function processing inputs from SQS and computing moving-averages in time, uses 2 Lambda functions
4. DynamoDB - storage for broken sensors, used by sensor lambda
5. Trigger Sensor Script - script simulating real-world data generating process, by sending requests with random inputs with random intervals
6. Terraform Lambda Module - generic IaC set-up for Lambda functions, used by all Lambda functions in the application
7. Terragrunt - IaC orchestrator for terraform using configuration parameterized by YAML files to deploy `dev` and `prod` environments
