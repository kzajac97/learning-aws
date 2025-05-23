resource "aws_dynamodb_table" "sensor_registry" {
  name         = "sensor-registry-${local.env}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor_id"

  attribute {
    name = "sensor_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "sensor_lambda_persistence_layer" {
  name         = "sensor-lambda-persistence-${local.env}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = "expiration"
    enabled        = true
  }
}
