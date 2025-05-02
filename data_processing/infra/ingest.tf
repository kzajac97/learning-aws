locals {
  local_ingest_script_path = "${path.module}/../src/glue/ingest.py"
}

resource "aws_s3_object" "glue_ingest_script_source" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "${var.scripts_directory}/ingest.py"
  source = local.local_ingest_script_path

  source_hash = filemd5(local.local_ingest_script_path)
}

resource "aws_glue_job" "glue_ingest" {
  name     = "dps-ingest"
  role_arn = data.aws_iam_role.main_role.arn

  worker_type       = "G.1X"
  number_of_workers = 2

  max_retries  = 1
  timeout      = 10
  glue_version = "5.0"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_object.glue_scripts.bucket}/${aws_s3_object.glue_ingest_script_source.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--TempDir"                          = "s3://${aws_s3_object.sparklogs.bucket}/${aws_s3_object.sparklogs.key}"
    "--JOB_NAME"                         = "dps-ingest"
    "--glue_database"                    = aws_glue_catalog_database.data_processing_db.name
    "--input_glue_table_name"            = aws_glue_catalog_table.raw_glue_table.name
    "--output_glue_table_name"           = aws_glue_catalog_table.processed_glue_table.name
    "--source_label"                     = "default"
  }
}
