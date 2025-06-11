# Process New Invoice End-to-End

Complete workflow to process a new invoice PDF through the entire system pipeline.

## What this does:
1. Ask for the invoice PDF file path
2. Extract structured data using vision MCP
3. Match or create vendor in QuickBooks
4. Auto-code line items based on chart of accounts
5. Optionally post to QuickBooks as a bill
6. Save results and provide summary

## Actions:
- Prompt user for PDF file path (in test-documents/ folder)
- Run `mcp__vision__extractInvoiceData(file_path)`
- Run `mcp__quickbooks-server__matchVendorFromInvoice(invoice_data)`
- Run `mcp__quickbooks-server__autoCodeInvoice(invoice_data)`
- Ask if user wants to post to QuickBooks
- If yes, run `mcp__quickbooks-server__postInvoiceToQuickBooks(coded_data)`
- Show summary of what was processed and where results are saved

This is the main workflow for processing new invoices.