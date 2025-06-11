# Process Invoice End-to-End

Process a PDF invoice through the complete workflow: extract → match vendor → code → post to QuickBooks

## Usage
Use this command when you have a new invoice PDF that needs to be processed and posted to QuickBooks.

## Steps
1. Extract structured data from PDF using vision MCP
2. Match or create vendor in QuickBooks
3. Auto-code line items based on chart of accounts
4. Post as bill to QuickBooks
5. Optionally add vendor to CRM for future tracking

## Example
```bash
# Process invoice end-to-end
mcp__quickbooks-server__processInvoiceEnd2End("test-documents/invoice.pdf", auto_post=false)

# Or step by step:
# 1. Extract data
mcp__vision__extractInvoiceData("test-documents/invoice.pdf")

# 2. Match vendor (use extracted data from step 1)
mcp__quickbooks-server__matchVendorFromInvoice(invoice_data)

# 3. Auto-code invoice
mcp__quickbooks-server__autoCodeInvoice(invoice_data)

# 4. Post to QuickBooks
mcp__quickbooks-server__postInvoiceToQuickBooks(coded_data, auto_post=true)
```

## Files
- Input: PDF files in `test-documents/`
- Output: Structured JSON in `output/invoices/`
- QuickBooks: Posted as Bills