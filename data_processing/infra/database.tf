variable "db_name" {
  type        = string
  description = "RDS database name"
  default     = "survey"
}

variable "db_username" {
  type        = string
  description = "RDS username"
  default     = "dbuser"
}

variable "password" {
  type        = string
  description = "RDS password (secret)"
  sensitive   = true
}

resource "aws_ssm_parameter" "db_name" {
  name = "/db/name"
  type = "String"
  value = var.db_name
}

resource "aws_ssm_parameter" "db_user" {
  name = "/db/user"
  type = "String"
  value = var.db_username
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/db/password"
  type  = "SecureString"
  value = var.password
}

resource "aws_db_instance" "postgres" {
  identifier     = "survey-postgres"
  db_name        = var.db_name
  engine         = "postgres"
  engine_version = "17.2"

  instance_class = "db.t4g.micro"

  allocated_storage = 10
  storage_type      = "gp2"

  username = var.db_username
  password = var.password

  skip_final_snapshot = true
  publicly_accessible = true

  vpc_security_group_ids = [aws_security_group.rds_restricted.id]
}

resource "aws_ssm_parameter" "db_host" {
  name  = "/db/host"
  type  = "SecureString"
  value = aws_db_instance.postgres.endpoint
}

resource "aws_ssm_parameter" "db_port" {
  name  = "/db/port"
  type  = "String"
  value = aws_db_instance.postgres.port
}
