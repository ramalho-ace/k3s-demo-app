#!/bin/bash
# Script para build e push da imagem para Artifact Registry
# Uso: ./build-and-push.sh [VERSION]
#   Se VERSION não for fornecido, usa 'latest'

set -e

PROJECT_ID="offshore-hub-foundations"
REGION="southamerica-east1"
REPO_NAME="offshore-hub-repo"
IMAGE_NAME="python-app"
VERSION="${1:-latest}"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${VERSION}"

echo "🔨 Building image: $IMAGE_URL"

# Build da imagem
docker build -t "$IMAGE_URL" .

echo "✅ Image built successfully"

# Autenticar no Artifact Registry
echo "🔐 Authenticating to Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Push da imagem
echo "📤 Pushing image to Artifact Registry..."
docker push "$IMAGE_URL"

echo "✅ Image pushed successfully: $IMAGE_URL"
