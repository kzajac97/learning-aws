resource "aws_sqs_queue" "sensor_queue" {
  name                        = "sensor_queue"
  visibility_timeout_seconds  = 5 * 60  # 5 minutes
  message_retention_seconds   = 5 * 60  # 5 minutes
}

resource "aws_sfn_state_machine" "sensor_state_machine" {
  name     = "sensor_state_machine"
  role_arn = data.aws_iam_role.main_role.arn

  definition = jsonencode({
    Comment = "A simple state machine that does nothing for now",
    StartAt = "Pass",
    States = {
      Pass = {
        Type = "Pass",
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

resource "aws_sqs_queue_policy" "sensor_queue_policy" {
  queue_url = aws_sqs_queue.sensor_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sqs:SendMessage",
        Resource = aws_sqs_queue.sensor_queue.arn
      }
    ]
  })
}