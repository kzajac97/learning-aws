locals {
  script_filename = basename(var.script_path)
}

resource "aws_s3_object" "glue_script_source" {
  bucket = var.glue_assets_bucket
  key    = "${var.scripts_directory}/${local.script_filename}"
  source = var.script_path

  source_hash = filemd5(var.script_path)
}


resource "aws_glue_job" "etl" {
  name     = var.name
  role_arn = var.role_arn

  worker_type       = var.worker_type
  number_of_workers = var.num_workers

  max_retries  = var.max_retries
  timeout      = var.timeout
  glue_version = "5.0"

  command {
    name            = "glueetl"
    script_location = "s3://${var.glue_assets_bucket}/${aws_s3_object.glue_script_source.key}"
    python_version  = "3"
  }

  default_arguments = merge(
    {
      "--enable-metrics"                   = "true"
      "--enable-continuous-cloudwatch-log" = "true"
      "--TempDir"                          = "s3://${var.glue_assets_bucket}/sparklogs/"
      "--JOB_NAME"                         = var.name
    },
    var.arguments
  )

  tags = {
    env = var.env
  }
}