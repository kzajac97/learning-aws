resource "aws_s3_object" "glue_etl_script_source" {
  bucket = aws_s3_bucket.glue_assets.bucket
  key    = "${aws_s3_object.glue_scripts.key}/ingest.py"
  source = "${path.module}/../src/ingest.py"

  lifecycle {
    create_before_destroy = true
  }
}

resource "null_resource" "force_recreate" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "echo 'Forcing S3 object recreation'"
  }

  depends_on = [aws_s3_object.glue_etl_script_source]
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
    script_location = "s3://${aws_s3_object.glue_scripts.bucket}/${aws_s3_object.glue_etl_script_source.key}"
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
