# Brokerage Document Processor UI

A beautiful web interface for extracting structured data from brokerage statements using AI-powered vision processing.

## Features

- **Drag & Drop Interface**: Simply drag PDF files into the browser
- **Real-time Processing**: Watch as AI extracts data with live progress updates
- **Beautiful Results Display**: View extracted data in a clean, structured format
- **Error Handling**: Clear feedback when processing fails
- **Raw Data View**: Toggle between structured view and raw extracted text

## Quick Start

From the project root directory:

```bash
./start-ui.sh
```

This will:
1. Install all dependencies for both API and frontend
2. Start the API server on port 3001
3. Start the frontend on port 3000
4. Open your browser to http://localhost:3000

## Manual Setup

If you prefer to run components separately:

### 1. Start API Server
```bash
cd web-app/api
npm install
npm start
```

### 2. Start Frontend
```bash
cd web-app/frontend
npm install
npm run dev
```

## How It Works

1. **Upload**: Drag a PDF brokerage statement into the web interface
2. **Process**: The file is saved to `/test-documents` and processed by the Vision MCP server
3. **Extract**: AI extracts structured data including:
   - Statement metadata (provider, dates, type)
   - Customer information (name, account, address)
   - Account holdings (securities, quantities, values)
   - Total portfolio value
4. **Review**: View the extracted data in a beautiful interface
5. **Export**: Structured data is automatically saved as JSON in `/output/brokerage`

## Supported Documents

- Fidelity brokerage statements
- Charles Schwab statements
- E*TRADE statements
- Other major brokerage providers

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Express.js + Multer
- **AI Processing**: OpenAI Vision API via MCP server
- **Design**: Jony Ive-inspired minimalist interface

## File Structure

```
web-app/
├── api/
│   ├── package.json
│   └── server.js          # Express API server
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main app component
│   │   ├── components/
│   │   │   ├── DragDrop.jsx   # Upload interface
│   │   │   └── ReviewPage.jsx # Results display
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Environment Requirements

- Node.js 18+
- Python 3.8+ (for MCP server)
- OpenAI API key (configured in MCP server)

## Troubleshooting

**API Server won't start:**
- Check that port 3001 is available
- Ensure Vision MCP server dependencies are installed

**File upload fails:**
- Verify `/test-documents` directory exists and is writable
- Check that only PDF files are being uploaded

**Processing fails:**
- Ensure OpenAI API key is configured
- Check Vision MCP server logs for errors
- Verify `/output/brokerage` directory exists

## Development

The frontend uses Vite for fast development with hot reloading. The API uses Node.js --watch for automatic restarts.

Both components are designed to work together but can be developed independently.