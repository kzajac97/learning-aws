data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "default" {
  vpc_id            = data.aws_vpc.default.id
  availability_zone = "us-east-1a"
}

data "aws_route_table" "default" {
  vpc_id = data.aws_vpc.default.id
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = data.aws_vpc.default.id
  service_name      = "com.amazonaws.us-east-1.s3"
  route_table_ids   = [data.aws_route_table.default.id]
  vpc_endpoint_type = "Gateway"
}

resource "aws_vpc_endpoint" "ec2_messages" {
  vpc_id            = data.aws_vpc.default.id
  service_name      = "com.amazonaws.us-east-1.ec2messages"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [data.aws_subnet.default.id]

  security_group_ids = [aws_security_group.rds_restricted.id]
}

resource "aws_security_group_rule" "allow_ssm" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.rds_restricted.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group" "rds_restricted" {
  name        = "rds-restricted-sg"
  description = "Allow only personal computer to RDS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432 # default for PostgreSQL
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${local.config.network.allowed_ip}/32"]
  }

  # Allow all traffic within the same security group (required for Glue)
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
