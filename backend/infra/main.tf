provider "aws" {
  region = "us-east-1"
  # shared_credentials_files = ["~/.aws/credentials"]
  # profile                  = "pwr"
}

resource "aws_s3_bucket" "s3" {
  bucket = "infra-shared-tf-backend"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_dynamodb_table" "locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }
}

terraform {
  backend "s3" {
    bucket         = "infra-shared-tf-backend"
    key            = "backend.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}