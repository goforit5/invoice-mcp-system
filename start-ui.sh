#!/bin/bash

echo "🚀 Starting Brokerage Document Processor UI..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
lsof -ti:3000,3001 | xargs kill -9 2>/dev/null || true
sleep 1

# Check if we're in the right directory
if [ ! -d "web-app" ]; then
    echo "❌ Error: web-app directory not found. Make sure you're in the project root."
    exit 1
fi

# Function to install dependencies if needed
install_deps() {
    local dir=$1
    local name=$2
    
    if [ ! -d "$dir/node_modules" ]; then
        echo "📦 Installing $name dependencies..."
        (cd "$dir" && npm install)
    else
        echo "✅ $name dependencies already installed"
    fi
}

# Install API dependencies
echo "🔧 Setting up API server..."
install_deps "web-app/api" "API"

# Install Frontend dependencies
echo "🎨 Setting up Frontend..."
install_deps "web-app/frontend" "Frontend"

echo ""
echo "🌟 Starting services..."
echo "   📡 API Server: http://localhost:3001"
echo "   🖥️  Frontend: http://localhost:3000"
echo ""

# Start API server in background
echo "⚡ Starting API server..."
(cd web-app/api && npm start) &
API_PID=$!

# Wait for API to start
sleep 3

# Test API
if curl -s http://localhost:3001/api/health > /dev/null; then
    echo "✅ API server started successfully"
else
    echo "❌ API server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Start frontend in foreground
echo "⚡ Starting frontend..."
echo "💡 Open http://localhost:3000 in your browser to use the app"
echo ""
cd web-app/frontend
npm run dev

# Clean up background process when frontend exits
echo ""
echo "🛑 Shutting down..."
kill $API_PID 2>/dev/null
echo "✅ Stopped API server"