# Backend

This simple application is terraform backend manager. It uses single S3 bucket and DynamoDB table to store state files
and locks for all applications in this repository (including itself).

*Note*: Backend in not managed via CI/CD. Changes need to be deployed manually and resource deletion is prevented by
terraform lifecycle.

### First Creation

To create the backend on new AWS account, comment-out the code for managing backend and only create S3 and DynamoDB
for managing the backend later, using the code below (add provider and required credentials as well).

1. Run `terraform init`
2. Run `terraform plan -out backend.tfp` (this saves plan into the file)
3. Run `terraform apply "backend.tf"` (create resource on AWS)

```terraform
resource "aws_s3_bucket" "data" {
  bucket = "infra-shared-tf-backend"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

### State Migration

After creating the backend successfully, its own state can be migrated to the S3 and DynamoDB. To do this, review the
created resources and follow the steps:

1. Run `terraform init -migrate-state` and confirm it with `"yes"`
2. Run `terraform plan` and verify, if S3 state is used and locks are properly acquired
