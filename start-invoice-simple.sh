#!/bin/bash

echo "🧾 Starting Invoice Processing UI (Simple Mode)..."

# Check if directories exist
if [ ! -d "invoice-app" ]; then
    echo "❌ Error: invoice-app directory not found."
    exit 1
fi

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "invoice-app" 2>/dev/null || true
lsof -ti:3002,3003 | xargs kill -9 2>/dev/null || true
rm -f *invoice*.pid *invoice*.log 2>/dev/null || true

echo ""
echo "🚀 Starting API server..."
echo "cd invoice-app/api && npm start"
echo ""
echo "🎨 In another terminal, run:"
echo "cd invoice-app/frontend && npm run dev"
echo ""
echo "📱 Then open: http://localhost:3003"
echo ""
echo "💡 Or run these commands manually:"
echo ""
echo "Terminal 1:"
echo "cd invoice-app/api"
echo "npm start"
echo ""
echo "Terminal 2:" 
echo "cd invoice-app/frontend"
echo "npm run dev"
echo ""