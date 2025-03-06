variable "aws_docker_registry_domain" {
  # https://github.com/aws/deep-learning-containers/blob/master/available_images.md
  description = "AWS Account ID, where pre-build images are stored"
  default     = "763104351884"
}

resource "aws_s3_object" "model_data" {
  bucket = var.model_data_bucket_name
  key    = var.model_data_key
  # add optionally for nested folders
  # source = var.model_data_key
}

resource "aws_sagemaker_model" "default" {
  name               = var.model_name
  execution_role_arn = aws_iam_role.default.arn

  container {
    image          = "${var.aws_docker_registry_domain}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/"
    model_data_url = "s3://${var.model_data_bucket_name}/${var.model_data_key}"
    environment = {
      HF_TASK                       = var.model_task,
      TS_MAX_RESPONSE_SIZE          = 13107000,
      TS_MAX_REQUEST_SIZE           = 13107000,
      MMS_MAX_RESPONSE_SIZE         = 13107000,
      MMS_MAX_REQUEST_SIZE          = 13107000,
      MMS_WORKERS_PER_MODEL         = 1,
      SAGEMAKER_CONTAINER_LOG_LEVEL = 20, # 20 is INFO
    }
  }
}

resource "aws_sagemaker_endpoint_configuration" "default" {
  name = "${var.endpoint_name}-configuration"

  # https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html
  production_variants {
    variant_name           = "variant-1"
    model_name             = aws_sagemaker_model.default.name
    initial_instance_count = var.instance_count
    instance_type          = var.instance_type
    initial_variant_weight = 1
  }
}

resource "aws_sagemaker_endpoint" "default" {
  name                 = var.endpoint_name
  endpoint_config_name = aws_sagemaker_endpoint_configuration.default.name
}
