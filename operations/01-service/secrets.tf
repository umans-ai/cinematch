# Secrets Manager
# Data source for existing secrets (created manually)

# TMDB API Key - must be created manually via AWS Console or CLI:
# aws secretsmanager create-secret --name cinematch/tmdb-api-key --secret-string "your-api-key" --region eu-west-1
data "aws_secretsmanager_secret" "tmdb_api_key" {
  name = "cinematch/tmdb-api-key"
}
