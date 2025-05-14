provider "aws" {
  region = "<<REGION>>"
}

data "aws_caller_identity" "current" {}


module "sagemaker_realtime_endpoint" {
  source = "./modules"
  # TODO: Fill in the required variables
  endpoint_name          = "<<ENDPOINT_NAME>>"
  model_data_bucket_name = "<<BUCKET_NAME>>"
  model_data_key         = "<<MODEL_DATA_KEY>>"
  model_name             = "<<MODEL_NAME>>"
  model_task             = "<<MODEL_TASK>>"
}
