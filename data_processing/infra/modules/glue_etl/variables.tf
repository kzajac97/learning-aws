variable "name" {
  type        = string
  description = "Name of the Glue ETL job"
}

variable "env" {
  type        = string
  description = "Environment name (e.g., dev, prod)"
}

variable "script_path" {
  type        = string
  description = "Relative path of script code"
}

variable "glue_assets_bucket" {
  type        = string
  description = "S3 bucket name for glue assets"
}

variable "scripts_directory" {
  type        = string
  description = "S3 path to the scripts directory"
}

variable "role_arn" {
  type        = string
  description = "IAM role ARN for the Glue job"
}

variable "num_workers" {
  type        = number
  description = "Number of workers for the Glue job"
  default     = 2
}

variable "worker_type" {
  type        = string
  description = "Type of worker for the Glue job"
  default     = "G.1X"
}

variable "logs_s3_uri" {
  type        = string
  description = "S3 URI for the logs"
}

variable "max_retries" {
  type        = number
  description = "Maximum number of retries for the Glue job"
  default     = 1
}

variable "timeout" {
  type        = number
  description = "Timeout for the Glue job in minutes"
  default     = 10
}

variable "arguments" {
  type        = map(string)
  description = "Arguments for the Glue job"
}
