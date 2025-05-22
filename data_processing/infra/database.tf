resource "aws_ssm_parameter" "db_name" {
  name  = "/db/name"
  type  = "String"
  value = local.config.db.name
}

resource "aws_ssm_parameter" "db_user" {
  name  = "/db/user"
  type  = "String"
  value = local.config.db.username
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/db/password"
  type  = "SecureString"
  value = local.config.db.password
}

resource "aws_db_instance" "postgres" {
  identifier     = "survey-postgres"
  db_name        = local.config.db.name
  engine         = "postgres"
  engine_version = "17.2"

  instance_class = "db.t4g.micro"

  allocated_storage = 10
  storage_type      = "gp2"

  username = local.config.db.username
  password = local.config.db.password

  skip_final_snapshot = true
  publicly_accessible = true

  vpc_security_group_ids = [aws_security_group.rds_restricted.id]
}

resource "aws_ssm_parameter" "db_host" {
  name  = "/db/endpoint"
  type  = "SecureString"
  value = aws_db_instance.postgres.endpoint
}

resource "aws_ssm_parameter" "db_port" {
  name  = "/db/port"
  type  = "String"
  value = aws_db_instance.postgres.port
}
