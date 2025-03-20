locals {
  report_frequency_min = 5
}

resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor_queue"
  visibility_timeout_seconds = local.report_frequency_min * 60
  message_retention_seconds  = 1 * 60 * 60 # 1 hour
}

data "archive_file" "consumer_lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/recievier_lambda"
  output_path = "${path.module}/recievier_lambda.zip"
}

resource "aws_lambda_function" "consumer_lambda" {
  filename         = data.archive_file.consumer_lambda_source_code.output_path
  function_name    = "consumer_lambda"
  role             = data.aws_iam_role.main_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.13"
  timeout          = 60
  source_code_hash = filebase64sha256(data.archive_file.consumer_lambda_source_code.output_path)

  environment {
    variables = {
      ENV     = "dev"
      SQS_URL = aws_sqs_queue.sensor_queue.id
    }
  }
}
