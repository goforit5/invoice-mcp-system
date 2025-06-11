# Invoice & Document Processing MCP System

## Project Overview
Multi-component AI-powered system for invoice processing, document analysis, and business automation with integrated MCP servers for Claude Code.

**Core Purpose**: Process invoices/documents → Extract data → Integrate with QuickBooks → Manage business relationships

## Architecture Map
```
claudecode1/
├── invoice-app/          # Simple invoice processor (React + Node)
├── web-app/             # Advanced brokerage document processor
├── src/
│   ├── vision/          # PDF/image extraction MCP server (OpenAI Vision)
│   ├── quickbooks/      # QuickBooks integration MCP server
│   ├── crm-db/          # Contact/communication management MCP server
│   ├── fetch/           # Web content fetching MCP server
│   └── playwright/      # Browser automation MCP server
├── test-documents/      # Sample PDFs for testing
└── output/             # Processed results (JSON)
```

## Available MCP Servers
1. **vision** - PDF/image text extraction and structured data analysis
2. **quickbooks** - Full QuickBooks integration for invoice posting
3. **crm-db** - Contact management and communication tracking
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
./start-invoice-simple.sh       # Invoice app (React + Node)
./start-ui.sh                  # Brokerage processor (advanced)
```

### MCP Server Operations
```bash
# Test individual servers
python src/vision/server.py
python src/crm-db/server.py
python src/quickbooks/server.py

# Test document processing
mcp__vision__extractInvoiceData("/path/to/invoice.pdf")
mcp__vision__extractbrokerage("/path/to/statement.pdf")
```

### Development Workflow
1. **Start Here**: `pwd && ls -la` (orient yourself)
2. **Check MCP**: `claude mcp list` (verify servers active)
3. **Test Documents**: Use files in `test-documents/` folder
4. **Process Flow**: vision → quickbooks → crm-db → output
5. **Results**: Check `output/invoices/` or `output/brokerage/`

## File Processing Patterns

### Invoice Processing Chain
```bash
# 1. Extract data from PDF
mcp__vision__extractInvoiceData("test-documents/invoice.pdf")

# 2. Match/create vendor in QuickBooks  
mcp__quickbooks-server__matchVendorFromInvoice(invoice_data)

# 3. Auto-code line items
mcp__quickbooks-server__autoCodeInvoice(invoice_data)

# 4. Post to QuickBooks
mcp__quickbooks-server__postInvoiceToQuickBooks(coded_data)

# 5. Track in CRM
# (Manual step - add vendor to CRM contacts)
```

### Document Analysis
- **Invoices**: `test-documents/*.pdf` → `output/invoices/*.json`
- **Brokerage**: `test-documents/*statement*.pdf` → `output/brokerage/*.json`

## Code Conventions

### Python (MCP Servers)
- Use FastMCP framework for all servers
- Include comprehensive error handling with try/catch
- Return JSON responses with success/error status
- Log all operations for debugging

### React/Node (UI Apps)
- Functional components with hooks
- Axios for API calls
- TailwindCSS for styling
- Express backends with CORS enabled

### File Handling
- Use absolute paths in configurations
- Save structured output to `output/` directory
- Keep original PDFs in `test-documents/`
- Use timestamps in output filenames

## Testing Strategy

### Quick Health Check
```bash
# Test each MCP server is responsive
mcp__vision__extractInvoiceData("test-documents/1240_001.pdf")
mcp__quickbooks-server__listVendors()
# Use search_contacts tool from crm-db

# Test UI apps
curl http://localhost:3001/api/health  # After starting apps
```

### Common Issues
- **MCP Not Working**: Check `claude mcp list`, restart Claude Code
- **Vision Errors**: Verify OpenAI API key in environment
- **QB Auth**: Re-run authentication if expired
- **File Paths**: Always use absolute paths for PDFs

## Environment Setup
- **Vision Server**: Requires OpenAI API key (already configured)
- **QuickBooks**: Requires sandbox/production credentials
- **CRM**: SQLite database (auto-initialized)
- **Node Apps**: Run `npm install` in each frontend/api directory

## Quick Start Checklist
1. ✅ Run `pwd && ls -la` to orient
2. ✅ Check `claude mcp list` shows all 5 servers
3. ✅ Test with sample document: `mcp__vision__extractInvoiceData`
4. ✅ Start UI if needed: `./start-ui.sh`
5. ✅ Monitor `output/` folder for results

**Remember**: This is an AI tool ecosystem. Each MCP server provides specialized capabilities for Claude Code to automate document processing workflows.