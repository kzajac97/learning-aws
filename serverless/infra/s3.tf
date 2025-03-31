resource "aws_s3_bucket" "sensor_data" {
  bucket = "sfn-sensor-analytics"
}

resource "aws_s3_bucket" "sfn_payloads" {
  bucket = "sfn-payloads"
}

resource "aws_s3_bucket_lifecycle_configuration" "example_lifecycle_policy" {
  bucket = aws_s3_bucket.sfn_payloads.id

  rule {
    id     = "expire-after-1-day"
    status = "Enabled"

    expiration {
      days = 1
    }

    filter {
    prefix = "" # Applies to all objects in the bucket
  }
  }
}
