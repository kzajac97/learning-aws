output "source_code_zip" {
  value = data.archive_file.source_code
}

output "function" {
  value = aws_lambda_function.function
}
