resource "aws_sns_topic" "sensor_notifications" {
  name = "sensor-notifications-${local.env}"
}

module "sensor_lambda" {
  source = "./modules/lambda"

  env              = local.env
  source_code_path = "${path.module}/../src/sensor_lambda"
  role_arn         = data.aws_iam_role.main_role.arn

  handler = "main.lambda_handler"
  runtime = "python3.13"

  max_parallel_executions = floor(0.4 * local.config["lambdas"]["max_parallel_executions"])

  env_variables = {
    SNS_TOPIC_ARN            = aws_sns_topic.sensor_notifications.arn
    SENSOR_REGISTRY_TABLE    = aws_dynamodb_table.sensor_registry.name
    SQS_URL                  = aws_sqs_queue.sensor_queue.id
    LAMBDA_IDEMPOTENCY_TABLE = aws_dynamodb_table.sensor_lambda_persistence_layer.name
  }
}
