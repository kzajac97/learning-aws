resource "aws_sqs_queue" "sensor_queue" {
  name                       = "sensor-queue-${local.env}"
  visibility_timeout_seconds = 0
  message_retention_seconds  = local.config["storage"]["message_retention_seconds"]
}
