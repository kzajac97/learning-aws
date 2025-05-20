locals {
  aws_region = get_env("AWS_REGION")
  config_path = get_env("CONFIG_PATH")
  # overwrite_python_path = get_env("OVERWRITE_PYTHON_PATH", "python")
}

remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = "infra-shared-tf-backend"
    key            = "serverless.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
}
EOF
}

inputs = {
  config_path = local.config_path
  aws_region = local.aws_region
  # overwrite_python_path = local.overwrite_python_path
}
