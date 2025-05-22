provider "aws" {
  region = "us-east-1"
}

provider "archive" {}

data "aws_iam_role" "main_role" {
  name = "LabRole"
}

locals {
  raw_config = yamldecode(file("${path.module}/config/secrets.yaml"))

  config = {
    db = {
      name     = local.raw_config["settings"]["db_name"]
      username = local.raw_config["settings"]["db_username"]
      password = sensitive(local.raw_config["secrets"]["db_password"])
    }
    network = {
      allowed_ip = sensitive(local.raw_config["secrets"]["allowed_ip"])
    }
  }
}

terraform {
  backend "s3" {
    bucket         = "infra-shared-tf-backend" # bucket created manually, shared between applications
    key            = "data-processing.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
