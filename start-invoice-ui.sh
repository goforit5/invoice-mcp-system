#!/bin/bash

# Invoice Processing UI Startup Script
# This script starts the Invoice Processor web interface

echo "🧾 Starting Invoice Processing UI..."

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Please stop the process using that port first."
        return 1
    fi
    return 0
}

# Function to start the API server
start_api() {
    echo "🚀 Starting Invoice API server on port 3002..."
    cd invoice-app/api
    
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing API dependencies..."
        npm install
    fi
    
    # Start the API server in background
    npm start > ../../api-invoice.log 2>&1 &
    API_PID=$!
    echo $API_PID > ../../api-invoice.pid
    echo "✅ API server started (PID: $API_PID)"
    cd ../..
}

# Function to start the frontend
start_frontend() {
    echo "🎨 Starting Invoice frontend on port 3003..."
    cd invoice-app/frontend
    
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Start the frontend in background
    npm run dev > ../../frontend-invoice.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../../frontend-invoice.pid
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
    cd ../..
}

# Function to check if services are running
wait_for_services() {
    echo "⏳ Waiting for services to start..."
    
    # Wait for API (max 30 seconds)
    for i in {1..30}; do
        if curl -s http://localhost:3002/api/health >/dev/null 2>&1; then
            echo "✅ API server is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ API server failed to start. Check api-invoice.log for details."
            exit 1
        fi
        sleep 1
    done
    
    # Wait for frontend (max 30 seconds)
    for i in {1..30}; do
        if curl -s http://localhost:3003 >/dev/null 2>&1; then
            echo "✅ Frontend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ Frontend failed to start. Check frontend-invoice.log for details."
            exit 1
        fi
        sleep 1
    done
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -d "invoice-app" ]; then
        echo "❌ Error: invoice-app directory not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check if required directories exist
    if [ ! -d "test-documents" ]; then
        echo "📁 Creating test-documents directory..."
        mkdir -p test-documents
    fi
    
    if [ ! -d "output/invoices" ]; then
        echo "📁 Creating output/invoices directory..."
        mkdir -p output/invoices
    fi
    
    if [ ! -d "data" ]; then
        echo "📁 Creating data directory..."
        mkdir -p data
    fi
    
    # Check ports
    if ! check_port 3002; then
        exit 1
    fi
    
    if ! check_port 3003; then
        exit 1
    fi
    
    # Start services
    start_api
    start_frontend
    wait_for_services
    
    echo ""
    echo "🎉 Invoice Processing UI is ready!"
    echo ""
    echo "🔗 Open your browser to: http://localhost:3003"
    echo ""
    echo "📊 API Status: http://localhost:3002/api/health"
    echo "📋 API Docs: http://localhost:3002/api/database"
    echo ""
    echo "📝 Logs:"
    echo "   API: tail -f api-invoice.log"
    echo "   Frontend: tail -f frontend-invoice.log"
    echo ""
    echo "🛑 To stop the servers:"
    echo "   kill \$(cat api-invoice.pid) \$(cat frontend-invoice.pid)"
    echo "   rm -f *.pid *.log"
    echo ""
    
    # Try to open browser
    if command -v open >/dev/null 2>&1; then
        echo "🌐 Opening browser..."
        open http://localhost:3003
    elif command -v xdg-open >/dev/null 2>&1; then
        echo "🌐 Opening browser..."
        xdg-open http://localhost:3003
    else
        echo "💡 Please open http://localhost:3003 in your browser"
    fi
    
    echo ""
    echo "⭐ Ready to process invoices! Drag and drop PDF files to get started."
    echo ""
    echo "📊 Live processing logs will appear below:"
    echo "$(tput setaf 8)─────────────────────────────────────────────────────────────────$(tput sgr0)"
}

# Function to show live logs
show_live_logs() {
    # Show API logs in real-time with color coding
    tail -f api-invoice.log 2>/dev/null | while IFS= read -r line; do
        if [[ "$line" == *"File uploaded:"* ]]; then
            echo "$(tput setaf 2)📄 $line$(tput sgr0)"
        elif [[ "$line" == *"Processing PDF"* ]]; then
            echo "$(tput setaf 3)⚙️  $line$(tput sgr0)"
        elif [[ "$line" == *"Python stderr: Processing file:"* ]]; then
            echo "$(tput setaf 4)🐍 $line$(tput sgr0)"
        elif [[ "$line" == *"Text extraction complete"* ]]; then
            echo "$(tput setaf 2)✅ $line$(tput sgr0)"
        elif [[ "$line" == *"Structured extraction complete"* ]]; then
            echo "$(tput setaf 2)✅ $line$(tput sgr0)"
        elif [[ "$line" == *"Saved to:"* ]]; then
            echo "$(tput setaf 2)💾 $line$(tput sgr0)"
        elif [[ "$line" == *"Error"* || "$line" == *"error"* ]]; then
            echo "$(tput setaf 1)❌ $line$(tput sgr0)"
        else
            echo "$(tput setaf 8)   $line$(tput sgr0)"
        fi
    done &
    TAIL_PID=$!
}

# Function to cleanup processes
cleanup() {
    echo "🛑 Stopping services..."
    
    # Kill tail process if running
    if [ ! -z "$TAIL_PID" ]; then
        kill $TAIL_PID 2>/dev/null
    fi
    
    # Kill processes by PID if files exist
    if [ -f "api-invoice.pid" ]; then
        API_PID=$(cat api-invoice.pid)
        if kill -0 $API_PID 2>/dev/null; then
            kill $API_PID 2>/dev/null
            echo "✅ Stopped API server (PID: $API_PID)"
        fi
    fi
    
    if [ -f "frontend-invoice.pid" ]; then
        FRONTEND_PID=$(cat frontend-invoice.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID 2>/dev/null
            echo "✅ Stopped frontend server (PID: $FRONTEND_PID)"
        fi
    fi
    
    # Also kill any remaining processes on the ports
    lsof -ti:3002 2>/dev/null | xargs -r kill -9 2>/dev/null
    lsof -ti:3003 2>/dev/null | xargs -r kill -9 2>/dev/null
    
    # Clean up files
    rm -f api-invoice.pid frontend-invoice.pid
    
    echo "🧹 Cleanup complete"
}

# Handle script interruption only (not normal exit)
trap cleanup INT TERM

# Run main function
main

# Start showing live logs
show_live_logs

# Keep script running and wait for user interrupt
echo "Press Ctrl+C to stop the servers..."
wait