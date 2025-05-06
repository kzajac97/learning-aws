provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "pwr"
}

provider "archive" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "data-processing-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

terraform {
  backend "s3" {
    bucket         = "infra-shared-tf-backend" # bucket created manually, shared between applications
    key            = "data-processing.tfstate"
    region         = "us-east-1"
    dynamodb_table = "data-processing-tf-locks"
    encrypt        = true
  }
}
