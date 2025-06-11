# QuickBooks MCP Server

A Model Context Protocol (MCP) server for complete QuickBooks integration and automated invoice processing.

## Features

- **Full QuickBooks API Integration**: Complete vendor and bill management
- **OAuth Authentication**: Secure authentication with credential persistence  
- **Intelligent Vendor Matching**: Automatic vendor matching from invoice data
- **Historical Coding Analysis**: Learn from past coding patterns
- **Automated Line Item Coding**: Smart account assignment based on description and history
- **End-to-End Processing**: Complete PDF-to-QuickBooks automation
- **Vision MCP Integration**: Seamless connection to PDF extraction services

## Setup

### 1. Install Dependencies

```bash
cd /Users/andrew/Projects/claudecode1/src/quickbooks
pip install -r requirements.txt
```

### 2. Configure QuickBooks App

1. Create a QuickBooks app at https://developer.intuit.com
2. Get your Client ID, Client Secret, and configure Redirect URI
3. Note your app's environment (sandbox/production)

### 3. Add to MCP Configuration

```bash
# Add the QuickBooks MCP server
claude mcp add quickbooks-server -e QB_ENV=sandbox -- /Users/andrew/Projects/claudecode1/src/quickbooks/server.py

# Or for project-wide access
claude mcp add quickbooks-server -s project -e QB_ENV=sandbox -- /Users/andrew/Projects/claudecode1/src/quickbooks/server.py
```

## Usage

### Initial Authentication

```python
# First time setup - authenticate with QuickBooks
result = authenticate(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    redirect_uri="your_redirect_uri",
    environment="sandbox"  # or "production"
)

# Follow the auth_url to complete OAuth flow
# Then your credentials will be saved for future use
```

### Basic Operations

```python
# Get all vendors
vendors = listVendors(active_only=True)

# Create new vendor
new_vendor = createVendor({
    "DisplayName": "Acme Supplies Inc.",
    "CompanyName": "Acme Supplies Inc.",
    "Address": {
        "Line1": "123 Supply St",
        "City": "San Francisco", 
        "CountrySubDivisionCode": "CA",
        "PostalCode": "94016"
    }
})

# Get chart of accounts
accounts = getChartOfAccounts(active_only=True)

# Create bill
bill = createBill({
    "VendorRef": {"value": "123", "name": "Acme Supplies"},
    "LineItems": [{
        "Amount": 125.50,
        "Description": "Office supplies",
        "AccountRef": {"value": "456", "name": "Office Expenses"}
    }]
})
```

### Automated Invoice Processing

```python
# Complete end-to-end processing
result = processInvoiceEnd2End(
    invoice_file_path="/path/to/invoice.pdf",
    auto_post=False  # Set to True for automatic posting
)

# Manual workflow steps
invoice_data = vision_mcp.extractInvoiceData("/path/to/invoice.pdf")
vendor_match = matchVendorFromInvoice(invoice_data["structured_data"])
coded_invoice = autoCodeInvoice(invoice_data["structured_data"], vendor_id="123")
post_result = postInvoiceToQuickBooks(coded_invoice, auto_post=True)
```

### Vendor Intelligence

```python
# Match vendor from invoice
match_result = matchVendorFromInvoice({
    "vendor_name": "Acme Supplies Inc.",
    "total_amount": 1250.75
})

# Get vendor's coding history
history = getVendorCodingHistory("123", limit=10)

# Auto-code based on patterns
coded = autoCodeInvoice(invoice_data, vendor_id="123")
```

## Integration with Vision MCP

This server is designed to work seamlessly with the Vision MCP server for complete automation:

1. **Vision MCP** extracts structured data from PDF invoices
2. **QuickBooks MCP** processes the data through the full workflow:
   - Vendor matching/creation
   - Historical pattern analysis  
   - Intelligent line item coding
   - Direct posting to QuickBooks

## Authentication & Security

- OAuth credentials are securely stored in `qb_auth.json` with restricted permissions
- Refresh tokens are automatically managed
- All API calls use the latest QuickBooks API version (v75)

## Error Handling

The server provides comprehensive error handling with detailed messages for:
- Authentication failures
- API rate limits
- Invalid data validation
- Network connectivity issues
- QuickBooks-specific errors

## Available Tools

- `authenticate`: Initial QuickBooks OAuth setup
- `listVendors`: Get all vendors with filtering
- `createVendor`: Create new vendor  
- `updateVendor`: Update existing vendor
- `listBills`: Get bills with filtering
- `createBill`: Create new bill
- `updateBill`: Update existing bill
- `getChartOfAccounts`: Get all accounts
- `matchVendorFromInvoice`: Intelligent vendor matching
- `getVendorCodingHistory`: Historical coding patterns
- `autoCodeInvoice`: Automated line item coding
- `postInvoiceToQuickBooks`: Post coded invoice as bill
- `processInvoiceEnd2End`: Complete automation workflow