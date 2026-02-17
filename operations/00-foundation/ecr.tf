# ECR Repositories
# Container registries for backend and frontend images
# Images are tagged per environment (production, pr-123, etc.)

resource "aws_ecr_repository" "backend" {
  name                 = "cinematch-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # Allow deletion for cleanup
}

resource "aws_ecr_repository" "frontend" {
  name                 = "cinematch-frontend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

# Lifecycle policy to cleanup old images
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
