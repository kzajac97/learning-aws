provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "pwr"
}

provider "archive" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}
