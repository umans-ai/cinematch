# Secrets Manager
# Store sensitive configuration like API keys

# TMDB API Key - stored as a secret
# Note: The secret value must be set manually via AWS Console or CLI after creation
resource "aws_secretsmanager_secret" "tmdb_api_key" {
  name        = "cinematch/tmdb-api-key"
  description = "TMDB API Key for CineMatch"

  tags = {
    Environment = terraform.workspace
    ManagedBy   = "terraform"
  }
}

# Placeholder secret version - this creates an empty secret
# The actual value should be set manually via AWS Console:
# aws secretsmanager put-secret-value --secret-id cinematch/tmdb-api-key --secret-string "your-api-key"
resource "aws_secretsmanager_secret_version" "tmdb_api_key" {
  secret_id     = aws_secretsmanager_secret.tmdb_api_key.id
  secret_string = "placeholder-replace-with-real-key"

  lifecycle {
    ignore_changes = [secret_string]
  }
}
