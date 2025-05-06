provider "aws" {
  region = "us-east-1"
}

provider "archive" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}

terraform {
  backend "s3" {
    bucket         = "infra-shared-tf-backend"
    key            = "serverless.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
