variable "password" {
  type        = string
  description = "RDS password (secret)"
  sensitive   = true
}

variable "public_ip" {
  type        = string
  description = "Public IP of the machine to allow access to RDS"
  sensitive   = true
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "rds_restricted" {
  name        = "rds-restricted-sg"
  description = "Allow only personal computer to RDS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432 # default for PostgreSQL
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${var.public_ip}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
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
