resource "aws_dynamodb_table" "sensor_registry" {
  name         = "sensor-registry-${local.env}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor_id"

  attribute {
    name = "sensor_id"
    type = "S"
  }
}
