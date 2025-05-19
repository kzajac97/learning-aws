# AWS Lambda Terraform Module

This module creates a simple AWS Lambda function using python and ZIP source code. It allows configuring the core
runtime properties, such as handler, python version (will not work with other runtimes, due to `pip` usage) and timeout.

**Note**: AWS Lambda function name is copied from the source code directory name (with convention changed from
snake_case to kebab-case).

### Build

The ZIP is built in the following steps:
1. Copy the entire directory from a source code path to a temporary directory
2. Copy every shared path from a list of `shared` paths to the temporary directory
3. Run `pip install` on the temporary directory from the `requirements.txt` file, if it exists
4. Create a ZIP file from the temporary directory

This module does not test the path shadowing or name collisions. It is the user's responsibility to ensure that the
shared paths do not conflict with the source code.

Build script is using python, so make sure it is added on your PATH and aliased as `python`.

### Raw Terraform

Example of ZIP lambda using Terraform resources, without the module.

```terraform
data "archive_file" "lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/../src/example_lambda"
  output_path = "${path.module}/.src/example_lambda.zip"
}

resource "aws_lambda_function" "example" {
  filename         = data.archive_file.lambda_source_code.output_path
  function_name    = "example"
  role             = data.aws_iam_role.main_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.13"
  source_code_hash = filebase64sha256(data.archive_file.lambda_source_code.output_path)

  environment {
    variables = {
      ENV = "dev"
    }
  }
}
```
