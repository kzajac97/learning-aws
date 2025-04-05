locals {
  report_frequency_min = 5
}

resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor_queue"
  visibility_timeout_seconds = local.report_frequency_min * 60
  message_retention_seconds  = 1 * 60 * 60 # 1 hour
}
