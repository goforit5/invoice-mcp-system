# Start Applications

Launch the invoice processing or brokerage document UIs

## Usage
Use when you need to start the web interfaces for document processing.

## Invoice App (Simple)
```bash
# Manual start (recommended for development)
cd invoice-app/api && npm start
# In another terminal:
cd invoice-app/frontend && npm run dev
# Open: http://localhost:3003

# Or use script:
./start-invoice-simple.sh
```

## Web App (Advanced Brokerage)
```bash
# Automatic start with health checks
./start-ui.sh
# Opens: http://localhost:3000
```

## Health Checks
```bash
# Check if apps are running
curl http://localhost:3001/api/health  # Web app API
curl http://localhost:3002/health      # Invoice app API (if running)

# Check ports in use
lsof -i :3000,3001,3002,3003
```

## Troubleshooting
- **Port conflicts**: Kill existing processes with `lsof -ti:3000 | xargs kill -9`
- **Dependencies**: Run `npm install` in each frontend/api directory
- **CORS errors**: Verify API server is running on correct port

## Stopping
```bash
# Kill all related processes
pkill -f "invoice-app\|web-app"
lsof -ti:3000,3001,3002,3003 | xargs kill -9
```