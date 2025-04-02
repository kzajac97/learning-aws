data "archive_file" "receiver_lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/recievier_lambda"
  output_path = "${path.module}/.src/recievier_lambda.zip"
}

resource "aws_lambda_function" "receiver_lambda" {
  filename                       = data.archive_file.receiver_lambda_source_code.output_path
  function_name                  = "sensor-analytics-receiver"
  role                           = data.aws_iam_role.main_role.arn
  handler                        = "main.handler"
  runtime                        = "python3.13"
  timeout                        = 60
  memory_size                    = 1024
  source_code_hash               = filebase64sha256(data.archive_file.receiver_lambda_source_code.output_path)
  reserved_concurrent_executions = 1

  # so far hardcoded layer ARN for pandas
  layers = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python313:1"]

  environment {
    variables = {
      ENV            = "dev"
      SQS_URL        = aws_sqs_queue.sensor_queue.id
      INPUT_BUCKET   = aws_s3_bucket.sensor_data.bucket
      PAYLOAD_BUCKET = aws_s3_bucket.sfn_payloads.bucket
    }
  }
}

data "archive_file" "reporter_lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/reporter_lambda"
  output_path = "${path.module}/.src/reporter_lambda.zip"
}

resource "aws_lambda_function" "reporter_lambda" {
  filename                       = data.archive_file.reporter_lambda_source_code.output_path
  function_name                  = "sensor-analytics-batch-reporter"
  role                           = data.aws_iam_role.main_role.arn
  handler                        = "main.handler"
  runtime                        = "python3.13"
  timeout                        = 60
  memory_size                    = 1024
  source_code_hash               = filebase64sha256(data.archive_file.reporter_lambda_source_code.output_path)
  reserved_concurrent_executions = 8

  # so far hardcoded layer ARN for pandas
  layers = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python313:1"]

  environment {
    variables = {
      ENV            = "dev"
      PAYLOAD_BUCKET = aws_s3_bucket.sfn_payloads.bucket
    }
  }
}

resource "aws_sfn_state_machine" "sensor_analytics_workflow" {
  name     = "sensor-analytics-workflow"
  role_arn = data.aws_iam_role.main_role.arn

  definition = templatefile("${path.module}/sensor-analytics-workflow.asl.json", {
    receiver_lambda_arn = "${aws_lambda_function.receiver_lambda.arn}:$LATEST"
    reporter_lambda_arn = "${aws_lambda_function.reporter_lambda.arn}:$LATEST"
  })
}