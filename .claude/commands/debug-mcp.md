# Debug MCP Servers

Troubleshoot and verify MCP server functionality

## Usage
Use when MCP servers aren't responding or giving errors.

## Quick Diagnostics
```bash
# Check which servers are configured
claude mcp list

# Test each server individually
python src/vision/server.py --help
python src/crm-db/server.py
python src/quickbooks/server.py

# Test with simple operations
mcp__vision__extractInvoiceData("test-documents/1240_001.pdf")
# Use search_contacts tool from crm-db with query "test"
mcp__quickbooks-server__listVendors()
```

## Common Issues

### Vision Server
- **Error**: OpenAI API issues
- **Fix**: Check API key in environment
- **Test**: Extract from known good PDF

### QuickBooks Server  
- **Error**: Authentication expired
- **Fix**: Re-run authentication flow
- **Test**: List vendors to verify connection

### CRM Database
- **Error**: Database not found
- **Fix**: Run database initialization
- **Test**: Search for contacts

### Server Not Starting
- **Fix**: Check Python environments and dependencies
- **Commands**:
  ```bash
  # Check Python paths
  which python3
  
  # Check dependencies
  pip list | grep mcp
  pip list | grep fastmcp
  ```

## Environment Check
```bash
# Verify all paths exist
ls -la src/*/server.py
ls -la vision-mcp-env/bin/python3
ls -la test-documents/

# Check logs
tail -f *.log
```