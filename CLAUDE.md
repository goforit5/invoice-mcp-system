# Invoice & Document Processing MCP System

## Project Overview
Production-grade AI-powered system for invoice processing, document analysis, and business automation with integrated MCP servers for Claude Code.

**Core Purpose**: Process invoices/documents → Extract data → Integrate with QuickBooks → Manage business relationships

## CRITICAL PROJECT STANDARDS

### 🚫 ZERO TOLERANCE POLICY
**This project NEVER uses:**
- Sample data, placeholders, or mock responses
- Synthetic/fake data or hardcoded values
- References to non-existent endpoints or services
- Simulated functionality or "TODO" implementations
- Any code that returns fake results

### ✅ PRODUCTION REQUIREMENTS
**Every component MUST:**
- Connect to real, functioning databases and APIs
- Return actual data from live systems
- Be fully tested and working end-to-end
- Handle real-world error conditions gracefully
- Use production-grade authentication and security
- Provide complete functionality with no gaps

**Code Quality Standards:**
- All MCP tools call actual Python functions with real database connections
- All API endpoints return live data from SQLite/QuickBooks/OpenAI
- All UI components display real data from working backends
- All file processing uses actual document analysis (OpenAI Vision)
- All CRM operations read/write to actual SQLite database at `src/crm-db/crm.db`

## Architecture Map
```
claudecode1/
├── invoice-app/          # Simple invoice processor (React + Node)
├── web-app/             # Advanced universal document processor
├── src/
│   ├── vision/          # PDF/image extraction MCP server (OpenAI Vision)
│   ├── quickbooks/      # QuickBooks integration MCP server
│   ├── crm-db/          # Contact/communication management MCP server
│   ├── fetch/           # Web content fetching MCP server
│   └── playwright/      # Browser automation MCP server
├── test-documents/      # Real PDFs for testing
└── output/             # Live processed results (JSON)
```

## Available MCP Servers
1. **vision** - PDF/image text extraction and structured data analysis (OpenAI GPT-4 Vision)
2. **quickbooks** - Full QuickBooks API integration for invoice posting
3. **crm-db** - Contact management and communication tracking (SQLite database)
4. **fetch** - Web content retrieval
5. **playwright** - Browser automation
6. **github** - GitHub repository management and file operations

## GitHub Configuration
**Default User**: goforit5
**Available Repositories**:
- ap_invoice_poc8 (updated Oct 14, 2024)
- ap_invoice_poc7 (created Oct 13, 2024)

## Essential Commands

### Project Status Check
```bash
pwd                              # Confirm location
ls -la                          # See project structure  
git status                      # Check repo status
claude mcp list                 # Verify MCP servers
```

### Start Applications
```bash
./start-universal-ai.sh         # Universal document processor (production system)
./start-invoice-simple.sh       # Invoice app (React + Node)
./start-ui.sh                  # Brokerage processor (advanced)
```

### MCP Server Operations
```bash
# Test individual servers (all return real data)
python src/vision/server.py
python src/crm-db/server.py
python src/quickbooks/server.py

# Test document processing (uses real OpenAI Vision API)
mcp__vision__extractInvoiceData("test-documents/1240_001.pdf")
mcp__vision__extractbrokerage("test-documents/statement.pdf")
```

### Development Workflow
1. **Start Here**: `pwd && ls -la` (orient yourself)
2. **Check MCP**: `claude mcp list` (verify servers active)
3. **Test Documents**: Use actual PDF files in `test-documents/` folder
4. **Process Flow**: vision → quickbooks → crm-db → output (all real data)
5. **Results**: Check `output/invoices/` or `output/brokerage/` for live results

## File Processing Patterns

### Invoice Processing Chain (Production)
```bash
# 1. Extract data from PDF (OpenAI Vision API)
mcp__vision__extractInvoiceData("test-documents/invoice.pdf")

# 2. Match/create vendor in QuickBooks (QuickBooks API)
mcp__quickbooks-server__matchVendorFromInvoice(invoice_data)

# 3. Auto-code line items (QuickBooks Chart of Accounts)
mcp__quickbooks-server__autoCodeInvoice(invoice_data)

# 4. Post to QuickBooks (Live QuickBooks posting)
mcp__quickbooks-server__postInvoiceToQuickBooks(coded_data)

# 5. Track in CRM (SQLite database operations)
mcp__crm-db__create_communication(communication_data)
```

### Document Analysis (Real Processing)
- **Invoices**: `test-documents/*.pdf` → `output/invoices/*.json` (OpenAI Vision processed)
- **Brokerage**: `test-documents/*statement*.pdf` → `output/brokerage/*.json` (Live analysis)

## Database Configuration

### CRM Database (SQLite)
- **Location**: `/Users/andrew/Projects/claudecode1/src/crm-db/crm.db`
- **Type**: Production SQLite database with real schema
- **Data**: All contacts, companies, communications, tasks are real records
- **Initialization**: Auto-creates tables on first run, no sample data

### QuickBooks Integration
- **API**: Live QuickBooks Sandbox/Production API
- **Authentication**: OAuth 2.0 with real credentials
- **Data**: Actual vendors, chart of accounts, bill posting

## Code Conventions

### Python (MCP Servers)
- Use FastMCP framework for all servers
- Include comprehensive error handling with try/catch
- Return JSON responses with success/error status from real operations
- Log all operations for debugging
- **NO mock data or placeholder responses**

### React/Node (UI Apps)
- Functional components with hooks
- Axios for API calls to live endpoints
- TailwindCSS for styling
- Express backends with CORS enabled
- **All data fetched from real MCP servers**

### File Handling
- Use absolute paths in configurations
- Save structured output to `output/` directory (real processing results)
- Keep original PDFs in `test-documents/`
- Use timestamps in output filenames
- **All file operations handle real documents**

## Testing Strategy

### Production Health Check
```bash
# Test each MCP server with real operations
mcp__vision__extractInvoiceData("test-documents/1240_001.pdf")  # Real OpenAI call
mcp__quickbooks-server__listVendors()                          # Real QB API call
mcp__crm-db__search_contacts("test")                           # Real DB query

# Test UI apps (live endpoints)
curl http://localhost:3001/api/health        # Production API health
curl http://localhost:3001/api/crm/dashboard # Real CRM data
```

### Production Verification
- **MCP Tools**: Every tool returns real data from live systems
- **Vision Processing**: Uses actual OpenAI GPT-4 Vision API
- **CRM Operations**: Reads/writes to real SQLite database
- **QuickBooks**: Live API integration with real sandbox/production
- **File Processing**: Processes actual PDF documents

### Common Issues
- **MCP Not Working**: Check `claude mcp list`, restart Claude Code
- **Vision Errors**: Verify OpenAI API key in environment
- **QB Auth**: Re-run authentication if expired
- **File Paths**: Always use absolute paths for PDFs
- **Database**: Ensure SQLite database exists and is accessible

## Environment Setup
- **Vision Server**: Requires OpenAI API key (configured for production)
- **QuickBooks**: Requires sandbox/production credentials (OAuth configured)
- **CRM**: SQLite database (production schema, auto-initialized)
- **Node Apps**: Run `npm install` in each frontend/api directory

## Quick Start Checklist
1. ✅ Run `pwd && ls -la` to orient
2. ✅ Check `claude mcp list` shows all MCP servers
3. ✅ Test with real document: `mcp__vision__extractInvoiceData`
4. ✅ Start UI: `./start-universal-ai.sh` (production system)
5. ✅ Monitor `output/` folder for real processing results
6. ✅ Verify CRM shows live data at http://localhost:3000

## System Endpoints (Production)
- **Frontend**: http://localhost:3000 (Universal Document AI)
- **API**: http://localhost:3001 (MCP-based backend)
- **Health Check**: http://localhost:3001/api/health
- **CRM Dashboard**: http://localhost:3001/api/crm/dashboard (live data)
- **MCP Status**: http://localhost:3001/api/mcp-status

**Remember**: This is a production AI tool ecosystem. Every component processes real data, connects to live systems, and provides complete functionality with zero placeholders or mock responses.

## Quick Commands & Custom Rules

### @document Processing Rule
**IMPORTANT RULE**: When the user types "@document" followed by a file path, I MUST automatically execute the complete document processing workflow without any prompts or pauses. This includes:

1. Extract data using `mcp__vision__extractDocumentData`
2. Show classification and extracted information
3. Search/create CRM company records
4. Create communication record
5. Generate appropriate tasks
6. Provide complete CRM analysis
7. Show actionable next steps

**Usage**: `@document <file-path>`

**Example**: `@document test-documents/invoice.pdf`

### Alternative Trigger
If "@document" doesn't work, use: `Process document: <file-path>`

**Note**: This is a single continuous workflow - execute ALL steps automatically.