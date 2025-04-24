variable "password" {
  type        = string
  description = "RDS password (secret)"
  sensitive   = true
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/db/password"
  type  = "SecureString"
  value = var.password
}

resource "aws_db_instance" "postgres" {
  identifier     = "survey-postgres"
  db_name        = "survey"
  engine         = "postgres"
  engine_version = "17.2"

  instance_class = "db.t4g.micro"

  allocated_storage = 10
  storage_type      = "gp2"

  username = "dbuser"
  password = aws_ssm_parameter.db_password.value

  skip_final_snapshot = true
  publicly_accessible = true

  vpc_security_group_ids = [aws_security_group.rds_restricted.id]
}
