# Process Any Document - Universal Document Processor

Complete automated workflow to process ANY document type through the intelligent document processing system with full CRM integration and analysis.

## AUTOMATED WORKFLOW STEPS:

### 1. Document Processing
- Extract document data using `mcp__vision__extractDocumentData(file_path)`
- Automatically classify document type (invoice, brokerage, DMV, legal, medical, tax, or general)
- Route to appropriate specialized extractor
- Save structured data to proper output folder

### 2. Classification Summary
- Show document type and confidence level
- Display which extractor was used
- Show extracted key information:
  - For invoices: vendor, amount, due date, invoice number
  - For brokerage: account info, holdings, transactions
  - For DMV: notice type, deadlines, required actions
  - For other types: key dates, parties, amounts, actions needed

### 3. CRM Integration
- Search for existing company/vendor in CRM
- Create company record if not found with all details
- Create communication record with full document content
- Create appropriate follow-up tasks:
  - Payment tasks for invoices
  - Review tasks for statements
  - Urgent tasks for time-sensitive documents
  - General follow-up tasks as needed

### 4. Workflow Automation
- Show which workflow was triggered
- Display all automated actions taken
- Report where results were saved
- List all CRM records created/updated

### 5. CRM Analysis & Summary
- Retrieve all created CRM records
- Analyze company profile and history
- Review communication details
- List all tasks with priorities and due dates
- Provide key insights:
  - Payment timelines
  - Relationship status
  - Historical patterns (if any)
  - Actionable recommendations

## USAGE:
When you @ mention this prompt with a file path, I will:
1. Process the document completely without stopping
2. Create all necessary CRM records
3. Generate tasks with appropriate due dates
4. Provide a comprehensive summary and analysis
5. Return actionable next steps

## EXAMPLE:
```
@process-any-document /Users/andrew/Projects/claudecode1/test-documents/invoice.pdf
```

This will automatically:
- Extract all data from the PDF
- Create vendor in CRM if needed
- Log the communication
- Create payment task
- Provide full analysis
- All in one continuous flow

## KEY BENEFITS:
- **Fully Automated**: No manual steps or prompts needed
- **Complete Integration**: Vision API → CRM → Task Management
- **Smart Classification**: Handles any document type intelligently
- **Comprehensive Analysis**: Full CRM data analysis included
- **One Command**: Single @ mention processes everything
- **Production Ready**: Uses real APIs and databases only

## SUPPORTED DOCUMENT TYPES:
- Invoices (vendor bills, utility bills, service invoices)
- Brokerage statements (Fidelity, Schwab, etc.)
- DMV notices (registration, tickets, notices)
- Legal documents (contracts, notices, agreements)
- Medical records (bills, reports, forms)
- Tax documents (forms, notices, statements)
- General documents (any other document type)

This prompt function provides complete document processing with full CRM integration and analysis in a single automated workflow.