locals {
  name      = lower(replace(basename(var.source_code_path), "_", "-"))
  build_dir = "${path.cwd}/.src/${local.name}"
}

resource "null_resource" "build_lambda" {
  triggers = {
    # trigger, when the directory does not exist
    dir_exists = length(fileset(var.source_code_path, "**")) > 0 ? "true" : "false"
    # trigger using sha256 hashes for each file in the source code directory using JSON encoding
    dir_hash = jsonencode({
      for file in fileset(var.source_code_path, "**") :
      file => filesha256("${var.source_code_path}/${file}")
    })
  }

  provisioner "local-exec" {
    # python script to build the lambda function, list of paths is passed as JSON
    command = "python ${path.module}/build.py --source ${var.source_code_path} --target ${local.build_dir} --shared ${jsonencode(var.shared_code_paths)}"
  }
}

data "archive_file" "source_code" {
  source_dir  = local.build_dir
  output_path = "${local.build_dir}/../${local.name}.zip" # add `..` to move the zip out of the build dir
  type        = "zip"

  depends_on = [null_resource.build_lambda]
}

resource "aws_lambda_function" "function" {
  # function name is the basename of directory with source code
  function_name = "${local.name}-${var.env}"
  role          = var.role_arn

  filename   = data.archive_file.source_code.output_path
  layers     = var.layers
  depends_on = [data.archive_file.source_code]

  handler                        = var.handler
  runtime                        = var.runtime
  memory_size                    = var.memory_size
  timeout                        = var.timeout
  reserved_concurrent_executions = var.max_parallel_executions

  # environment is given as mapping with additional ENV variable added
  environment {
    variables = merge(
      var.env_variables,
      {
        ENV = var.env
      }
    )
  }

  tags = {
    env = var.env
  }
}
