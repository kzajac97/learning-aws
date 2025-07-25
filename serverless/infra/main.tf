data "aws_iam_role" "main_role" {
  name = "LabRole"
}

variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
}

variable "config_path" {
  description = "Path to the configuration file"
  type        = string
}

locals {
  config = yamldecode(file(var.config_path))
  env    = local.config["env"] # name of the environment in given config
}
