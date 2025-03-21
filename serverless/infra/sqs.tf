locals {
  report_frequency_min = 5
}

resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor_queue"
  visibility_timeout_seconds = local.report_frequency_min * 60
  message_retention_seconds  = 1 * 60 * 60 # 1 hour
}

data "archive_file" "receiver_lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/recievier_lambda"
  output_path = "${path.module}/recievier_lambda.zip"
}

resource "aws_lambda_function" "consumer_lambda" {
  filename         = data.archive_file.receiver_lambda_source_code.output_path
  function_name    = "receiver_lambda"
  role             = data.aws_iam_role.main_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.13"
  timeout          = 60
  memory_size      = 1024
  source_code_hash = filebase64sha256(data.archive_file.receiver_lambda_source_code.output_path)

  # so far hardcoded layer ARN for pandas
  layers = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python313:1"]

  environment {
    variables = {
      ENV            = "dev"
      MAX_BATCH_SIZE = 100
      SQS_URL        = aws_sqs_queue.sensor_queue.id
    }
  }
}
