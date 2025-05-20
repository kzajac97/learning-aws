variable "source_code_path" {
  type        = string
  description = "Path to the source code of the lambda function"
}

variable "shared_code_paths" {
  type        = list(string)
  description = "List of local libraries to include in the lambda package"
  default     = []
}

variable "handler" {
  type        = string
  description = "Handler of the lambda function"
  default     = "main.handler"
}

variable "runtime" {
  type        = string
  description = "Runtime of the lambda function"
  default     = "python3.13"
}

variable "memory_size" {
  type        = number
  description = "Memory size of the lambda function"
  default     = 128
}

variable "timeout" {
  type        = number
  description = "Timeout of the lambda function"
  default     = 5
}

variable "role_arn" {
  type        = string
  description = "ARN of the IAM role that the lambda function will assume"
}

variable "max_parallel_executions" {
  type        = number
  description = "Maximum number of parallel executions for the lambda function"
  default     = 1
}

variable "layers" {
  type        = list(string)
  description = "List of Lambda layers to attach to the function"
  default     = []
}

variable "env" {
  type        = string
  description = "Environment variable for the lambda function"
  default     = "dev"
}

variable "env_variables" {
  type        = map(string)
  description = "Environment variables for the lambda function"
  default     = {}
}

variable "build_python_path" {
  type        = string
  description = "Path to the Python executable to use for Lambda build script"
  default     = "python"
}
