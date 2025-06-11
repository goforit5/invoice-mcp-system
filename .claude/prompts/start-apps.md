# Start Invoice Processing Applications

Launch the web applications for invoice and document processing.

## What this does:
1. Check if any apps are already running
2. Kill existing processes if needed
3. Start the requested application
4. Verify it's running properly
5. Provide access URLs

## Actions:
- Ask user which app to start:
  - Simple Invoice App (React + Node)
  - Advanced Web App (Brokerage processor)
- Check for existing processes on ports 3000-3003
- Kill conflicts if found
- Start the selected application using appropriate script
- Verify health endpoints
- Show URLs to access the running app

Choose your application and I'll get it running for you.