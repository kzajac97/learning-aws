# SQS Queue Configuration
resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor_queue"
  visibility_timeout_seconds = 6 * 60  # ensure enough time for processing
  message_retention_seconds  = 10 * 60 # retain messages longer to avoid loss
}

# Step Function Configuration
resource "aws_sfn_state_machine" "sensor_state_machine" {
  name     = "sensor_state_machine"
  role_arn = data.aws_iam_role.main_role.arn

  definition = jsonencode({
    Comment = "A state machine processing batched sensor data",
    StartAt = "ProcessData",
    States = {
      ProcessData = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.sensor_processing_lambda.arn
        },
        End = true
      }
    }
  })
}

resource "aws_lambda_event_source_mapping" "lambda_to_sqs" {
  event_source_arn = aws_sqs_queue.sensor_queue.arn
  function_name    = aws_lambda_function.sensor_lambda.arn
  enabled          = true
}

resource "aws_lambda_function" "sensor_processing_lambda" {
  filename      = "sensor_processing_lambda.zip"
  function_name = "sensor_processing_lambda"
  role          = data.aws_iam_role.main_role.arn
  handler       = "sensor_processing_lambda.handler"
  runtime       = "python3.13"
}


# EventBridge rule to trigger every 5 minutes
resource "aws_cloudwatch_event_rule" "sqs_trigger" {
  name                = "sensor_sqs_trigger"
  schedule_expression = "rate(5 minutes)"
}

# EventBridge target: Lambda function that processes SQS messages
resource "aws_cloudwatch_event_target" "sqs_lambda_target" {
  rule      = aws_cloudwatch_event_rule.sqs_trigger.name
  arn       = aws_lambda_function.sensor_processing_lambda.arn
}

# Lambda permission to allow invocation by EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sensor_processing_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sqs_trigger.arn
}
