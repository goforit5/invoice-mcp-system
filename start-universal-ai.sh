#!/bin/bash

echo "🤖 Starting MCP-Based Universal Document AI System..."

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

# Install API dependencies (including sqlite3)
echo "🔧 Setting up Universal Document AI API..."
install_deps "web-app/api" "API"

# Install Frontend dependencies (including react-dropzone)
echo "🎨 Setting up Frontend with enhanced UI..."
install_deps "web-app/frontend" "Frontend"

echo ""
echo "🌟 Starting MCP-Based Universal Document AI System..."
echo "   📡 MCP API Server: http://localhost:3001"
echo "   🖥️  MCP Frontend: http://localhost:3000"
echo ""
echo "🤖 MCP-Based Features Available:"
echo "   • 100% MCP tool-based document processing"
echo "   • Agentic workflow execution with MCP tools"
echo "   • Real-time MCP tool call visualization"
echo "   • Vision MCP server integration (OpenAI)"
echo "   • CRM database MCP server integration"
echo "   • QuickBooks MCP server integration"
echo "   • Live MCP tool execution monitoring"
echo ""

# Start API server in background
echo "⚡ Starting MCP-Based Document AI API server..."
(cd web-app/api && npm start) &
API_PID=$!

# Wait for API to start
sleep 3

# Test API
if curl -s http://localhost:3001/api/health > /dev/null; then
    echo "✅ API server started successfully"
    echo "🔗 MCP API endpoints available:"
    echo "   • POST /api/agentic-process - MCP-based document processing"
    echo "   • POST /api/mcp-tool - Execute individual MCP tools"
    echo "   • GET  /api/mcp-tools - List available MCP tools"
    echo "   • GET  /api/mcp-status - MCP server status"
    echo "   • GET  /api/health - System health check"
else
    echo "❌ API server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Start frontend in foreground
echo "⚡ Starting MCP-Based Document AI frontend..."
echo "💡 Open http://localhost:3000 in your browser to access the MCP system"
echo ""
echo "📋 MCP System Capabilities:"
echo "   1. 📄 Drag & drop any PDF document"
echo "   2. 🤖 AI agent calls MCP tools for processing"
echo "   3. 👁️  Vision MCP server extracts text and data"
echo "   4. 👥 CRM MCP server creates contacts and communications"
echo "   5. 💰 QuickBooks MCP server handles accounting integration"
echo "   6. 📊 Real-time MCP tool execution visualization"
echo "   7. 🎛️  MCP server status and tool monitoring"
echo ""
cd web-app/frontend
npm run dev

# Clean up background process when frontend exits
echo ""
echo "🛑 Shutting down MCP-Based Document AI System..."
kill $API_PID 2>/dev/null
echo "✅ Stopped MCP API server"
echo "👋 MCP-Based Document AI System stopped"