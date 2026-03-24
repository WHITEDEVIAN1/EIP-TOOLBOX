#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "======================================"
echo "📦 Building ToolForge Frontend"
echo "======================================"
cd frontend
npm install
npm run build
cd ..

echo "======================================"
echo "🐍 Installing Backend Dependencies"
echo "======================================"
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "======================================"
echo "✅ Build Complete!"
echo "======================================"
