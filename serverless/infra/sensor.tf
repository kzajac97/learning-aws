resource "aws_sns_topic" "sensor_notifications" {
  name = "sensor_notifications"
}

module "sensor_lambda" {
  source = "./modules/lambda"

  env              = "dev"
  source_code_path = "${path.module}/../src/sensor_lambda"
  role_arn         = data.aws_iam_role.main_role.arn

  handler = "main.lambda_handler"
  runtime = "python3.13"

  env_variables = {
    SNS_TOPIC_ARN         = aws_sns_topic.sensor_notifications.arn
    SENSOR_REGISTRY_TABLE = aws_dynamodb_table.sensor_registry.name
    SQS_URL               = aws_sqs_queue.sensor_queue.id
  }
}
