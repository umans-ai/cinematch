# Application Load Balancer
# Per-environment ALB (production, pr-123, etc.)

resource "aws_lb" "cinematch" {
  name               = "cinematch-${terraform.workspace}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.terraform_remote_state.foundation.outputs.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "cinematch-${terraform.workspace}"
  }
}

# Target Groups
resource "aws_lb_target_group" "backend" {
  name        = "cinematch-backend-${terraform.workspace}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_target_group" "frontend" {
  name        = "cinematch-frontend-${terraform.workspace}"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = data.terraform_remote_state.foundation.outputs.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ALB Listener - HTTPS (primary)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.cinematch.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = data.terraform_remote_state.foundation.outputs.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# ALB Listener - HTTP (redirects to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.cinematch.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Backend API path routing
resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/health"]
    }
  }
}
