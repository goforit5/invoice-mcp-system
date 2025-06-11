# Quick MCP System Test

Run a fast health check on all MCP servers to verify they're working properly.

## What this does:
1. Tests vision server with a sample invoice
2. Tests QuickBooks server (list vendors)
3. Tests CRM database (search contacts)
4. Tests fetch server if needed
5. Reports success/failure for each

## Actions:
- Test `mcp__vision__extractInvoiceData` with "test-documents/1240_001.pdf"
- Test `mcp__quickbooks-server__listVendors()`
- Test CRM search functionality
- Check for any error messages
- Provide a quick pass/fail summary

This is for when you want to quickly verify all systems are operational.