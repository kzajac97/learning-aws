locals {
  report_frequency_min = 60
}

resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor_queue"
  visibility_timeout_seconds = 0
  message_retention_seconds  = local.report_frequency_min
}
