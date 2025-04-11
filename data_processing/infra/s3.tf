resource "aws_s3_bucket" "raw_data" {
  bucket = "dps-ingest-data"
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "dps-processed-data"
}

resource "aws_s3_bucket" "glue_assets" {
  bucket = "dps-glue-assets"
}

resource "aws_s3_object" "sparklogs" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "sparklogs"
}

resource "aws_s3_object" "glue_scripts" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "scripts"
}