variable "raw_data_directory" {
  description = "The directory where the raw data is stored"
  type        = string
  default = "raw"
}

variable "processed_data_directory" {
  description = "The directory where the processed data is stored"
  type        = string
  default = "processed"
}

variable "normalized_data_directory" {
  description = "The directory where the normalized data is stored"
  type        = string
  default = "normalized"
}

variable "logs_directory" {
    description = "The directory where the logs are stored"
    type        = string
    default = "sparklogs"
}

variable "scripts_directory" {
    description = "The directory where the scripts are stored"
    type        = string
    default = "scripts"
}

resource "aws_s3_bucket" "data" {
  bucket = "dps-glue-data"
}

resource "aws_s3_bucket" "glue_assets" {
  bucket = "dps-glue-assets"
}

resource "aws_s3_object" "sparklogs" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "${var.logs_directory}/"
}

resource "aws_s3_object" "glue_scripts" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "${var.scripts_directory}/"
}

resource "aws_s3_object" "raw" {
  bucket = aws_s3_bucket.data.bucket
  key    = "${var.raw_data_directory}/"
}

resource "aws_s3_object" "processed" {
  bucket = aws_s3_bucket.data.bucket
  key    = "${var.processed_data_directory}/"
}

resource "aws_s3_object" "normalized" {
  bucket = aws_s3_bucket.data.bucket
  key    = "${var.normalized_data_directory}/"
}
