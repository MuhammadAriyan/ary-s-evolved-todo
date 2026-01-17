#!/bin/bash
# HuggingFace Spaces Deployment Script

echo "🚀 Deploying backend to HuggingFace Spaces..."
echo ""

# Check if HF_SPACE is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your HuggingFace Space path"
    echo "Usage: ./deploy-to-hf.sh username/space-name"
    echo "Example: ./deploy-to-hf.sh muhammadariyan/ary-todo-backend"
    exit 1
fi

HF_SPACE=$1
echo "📦 Deploying to: $HF_SPACE"
echo ""

# Check if hf CLI is available
if ! command -v hf &> /dev/null; then
    echo "❌ HuggingFace CLI not found. Installing..."
    pip install -U huggingface_hub
fi

# Upload backend to Space
echo "📤 Uploading backend files..."
hf upload "$HF_SPACE" . . --repo-type space --exclude ".git/*" --exclude "__pycache__/*" --exclude "*.pyc" --exclude ".env"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Your Space: https://huggingface.co/spaces/$HF_SPACE"
echo "🏥 Health check: https://${HF_SPACE/\//-}.hf.space/health"
echo ""
echo "⚙️  Next steps:"
echo "1. Go to https://huggingface.co/spaces/$HF_SPACE/settings"
echo "2. Add Repository secrets:"
echo "   - DATABASE_URL"
echo "   - CORS_ORIGINS (your Vercel URL)"
echo "   - BETTER_AUTH_URL (your Vercel URL)"
echo "   - JWT_SECRET_KEY"
echo "   - AI_API_KEY (optional)"
echo "   - AI_BASE_URL (optional)"
echo "   - AI_MODEL (optional)"
echo "3. Wait 2-5 minutes for build to complete"
echo "4. Test health endpoint"
