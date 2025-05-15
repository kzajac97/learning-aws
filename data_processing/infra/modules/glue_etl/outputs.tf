output "etl" {
  value = aws_glue_job.etl
}

output "s3_script" {
  value = aws_s3_object.glue_script_source
}
