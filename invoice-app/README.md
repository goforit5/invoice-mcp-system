# Invoice Document Processor UI

A beautiful web interface for extracting structured data from invoices using AI-powered vision processing.

## Features

- **Drag & Drop Interface**: Simply drag PDF invoices into the browser
- **Real-time Processing**: AI extracts invoice data with progress feedback
- **Beautiful Results Display**: View extracted data in a clean, editable interface
- **Invoice Editing**: Interactive editing of extracted invoice fields and line items
- **Error Handling**: Clear feedback when processing fails
- **Raw Data View**: Toggle between structured view and raw extracted text
- **Invoice Database**: Track all processed invoices with statistics

## Quick Start

From the project root directory:

```bash
./start-invoice-ui.sh
```

This will:
1. Install all dependencies for both API and frontend
2. Start the API server on port 3002
3. Start the frontend on port 3003
4. Open your browser to http://localhost:3003

## Manual Setup

If you prefer to run components separately:

### 1. Start API Server
```bash
cd invoice-app/api
npm install
npm start
```

### 2. Start Frontend
```bash
cd invoice-app/frontend
npm install
npm run dev
```

## How It Works

1. **Upload**: Drag an invoice PDF into the web interface
2. **Process**: The file is saved to `/test-documents` and processed by the Vision MCP server
3. **Extract**: AI extracts structured data including:
   - Invoice metadata (number, dates, amounts)
   - Vendor information (name, address, contact details)
   - Customer information (name, address, account)
   - Line items (descriptions, quantities, rates, amounts)
   - Payment instructions (ACH, wire, check details)
   - Invoice totals (subtotal, tax, shipping, total)
4. **Review & Edit**: View and edit the extracted data in a beautiful interface
5. **Export**: Structured data is automatically saved as JSON in `/output/invoices`

## Supported Invoice Types

- Service invoices (contractors, consultants, freelancers)
- Product invoices (retail, wholesale, manufacturing)
- Utility bills (electricity, gas, water, internet)
- Professional services (legal, accounting, medical)
- Subscription services (software, memberships)
- Any PDF invoice with structured data

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Express.js + Multer
- **AI Processing**: OpenAI Vision API via MCP server
- **Design**: Jony Ive-inspired minimalist interface

## File Structure

```
invoice-app/
├── api/
│   ├── package.json
│   └── server.js          # Express API server
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main app component
│   │   ├── components/
│   │   │   ├── InvoiceUpload.jsx   # Upload interface
│   │   │   ├── InvoiceReview.jsx   # Results display & editing
│   │   │   └── InvoiceDatabase.jsx # Database view
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## API Endpoints

- **POST /api/upload** - Upload and process invoice PDF
- **GET /api/health** - Health check
- **GET /api/results** - List processed invoice files
- **GET /api/result/:filename** - Get specific invoice result
- **GET /api/database** - Get all processed invoices from database
- **GET /api/record/:id** - Get specific invoice record by ID
- **GET /api/stats** - Get processing statistics
- **PUT /api/invoice/:id** - Update invoice data

## Environment Requirements

- Node.js 18+
- Python 3.8+ (for MCP server)
- OpenAI API key (configured in MCP server)

## Key Features

### Invoice Editing
- Interactive editing of all extracted fields
- Add/remove line items dynamically
- Real-time validation and formatting
- Save changes back to database

### Database Tracking
- Complete audit trail of all processed invoices
- Processing cost tracking
- Automation rate statistics
- Status monitoring (Complete/Partial/Needs Review)

### Smart Extraction
- Handles various invoice formats and layouts
- Extracts complex payment instructions
- Identifies vendor and customer information
- Processes line items with quantities and pricing

## Troubleshooting

**API Server won't start:**
- Check that port 3002 is available
- Ensure Vision MCP server dependencies are installed

**File upload fails:**
- Verify `/test-documents` directory exists and is writable
- Check that only PDF files are being uploaded

**Processing fails:**
- Ensure OpenAI API key is configured
- Check Vision MCP server logs for errors
- Verify `/output/invoices` directory exists

**Database issues:**
- Check `/data/processed_invoices.csv` file permissions
- Ensure database directory exists

## Development

The frontend uses Vite for fast development with hot reloading. The API uses Node.js --watch for automatic restarts.

Both components are designed to work together but can be developed independently.

## Cost Optimization

- Processing costs are tracked per invoice
- Typical cost: $0.01-0.05 per invoice page
- Batch processing recommended for cost efficiency
- Detailed cost breakdowns available in database

## Security & Privacy

- Uploaded files are processed locally
- No data sent to third parties except OpenAI API
- Structured data stored locally in JSON format
- All sensitive information remains on your system