# Security Groups
# Per-environment security groups (ALB and ECS)

resource "aws_security_group" "alb" {
  name        = "cinematch-alb-${terraform.workspace}"
  description = "ALB for CineMatch ${terraform.workspace}"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cinematch-alb-${terraform.workspace}"
  }
}

resource "aws_security_group" "ecs" {
  name        = "cinematch-ecs-${terraform.workspace}"
  description = "ECS tasks for CineMatch ${terraform.workspace}"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 8000
    to_port         = 8000
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    protocol        = "tcp"
    from_port       = 3000
    to_port         = 3000
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cinematch-ecs-${terraform.workspace}"
  }
}
