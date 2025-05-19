resource "aws_s3_bucket" "sensor_data" {
  bucket = "sfn-sensor-analytics-${local.env}"
}

resource "aws_s3_bucket" "sfn_payloads" {
  bucket = "sfn-payloads-${local.env}"
}

resource "aws_s3_bucket_lifecycle_configuration" "example_lifecycle_policy" {
  bucket = aws_s3_bucket.sfn_payloads.id

  rule {
    id     = "expire-after-n-days"
    status = "Enabled"

    expiration {
      days = local.config["storage"]["payload_expiration_days"]
    }

    filter {
      prefix = "" # Applies to all objects in the bucket
    }
  }
}
