module "receiver_lambda" {
  source = "./modules/lambda"

  env              = local.env
  source_code_path = "${path.module}/../src/receiver_lambda"
  role_arn         = data.aws_iam_role.main_role.arn

  handler     = "main.handler"
  runtime     = "python3.13"
  timeout     = 60
  memory_size = 1024

  max_parallel_executions = 1

  env_variables = {
    SQS_URL        = aws_sqs_queue.sensor_queue.id
    INPUT_BUCKET   = aws_s3_bucket.sensor_data.bucket
    PAYLOAD_BUCKET = aws_s3_bucket.sfn_payloads.bucket
  }
}

module "reporter_lambda" {
  source = "./modules/lambda"

  env              = local.env
  source_code_path = "${path.module}/../src/reporter_lambda"
  role_arn         = data.aws_iam_role.main_role.arn

  handler     = "main.handler"
  runtime     = "python3.13"
  timeout     = 60
  memory_size = 1024

  layers = ["arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python313:1"]

  max_parallel_executions = floor(0.4 * local.config["lambdas"]["max_parallel_executions"])

  env_variables = {
    PAYLOAD_BUCKET = aws_s3_bucket.sfn_payloads.bucket
  }
}

resource "aws_sfn_state_machine" "sensor_analytics_workflow" {
  name     = "sensor-analytics-workflow-${local.env}"
  role_arn = data.aws_iam_role.main_role.arn

  definition = templatefile("${path.module}/sensor-analytics-workflow.asl.json", {
    receiver_lambda_arn = "${module.receiver_lambda.function.arn}:$LATEST"
    reporter_lambda_arn = "${module.reporter_lambda.function.arn}:$LATEST"
  })
}
