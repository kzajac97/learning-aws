data "archive_file" "lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/sensor_lambda"
  output_path = "${path.module}/sensor_lambda.zip"
}

resource "aws_sns_topic" "sensor_notifications" {
  name = "sensor_notifications"
}

resource "aws_lambda_function" "sensor_lambda" {
  filename         = data.archive_file.lambda_source_code.output_path
  function_name    = "sensor_lambda"
  role             = data.aws_iam_role.main_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.13"
  timeout          = 10
  source_code_hash = filebase64sha256(data.archive_file.lambda_source_code.output_path)

  environment {
    variables = {
      ENV                   = "dev"
      SNS_TOPIC_ARN         = aws_sns_topic.sensor_notifications.arn
      SENSOR_REGISTRY_TABLE = aws_dynamodb_table.sensor_registry.name
      SQS_URL               = aws_sqs_queue.sensor_queue.id
    }
  }
}

resource "aws_lambda_permission" "allow_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sensor_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.sensor_notifications.arn
}

resource "aws_sns_topic_subscription" "lambda_subscription" {
  topic_arn = aws_sns_topic.sensor_notifications.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.sensor_lambda.arn
}
