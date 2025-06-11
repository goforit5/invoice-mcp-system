# Process Any Document - Universal Document Processor

Complete workflow to process ANY document type through the intelligent document processing system with full automation.

## What this does:
1. Ask for the document PDF file path
2. Automatically classify document type (invoice, brokerage, DMV, legal, medical, tax, or general)
3. Route to appropriate specialized extractor or use general extraction
4. Extract structured data based on document type
5. Automatically trigger appropriate workflows (DMV processing, invoice processing, etc.)
6. Save organized results to proper output folder
7. Create CRM records and tasks as needed
8. Provide complete processing summary

## Actions:
- Prompt user for PDF file path (in test-documents/ folder)
- Run `mcp__vision__extractDocumentData(file_path)` - this handles everything automatically!
- Show classification result and which extractor was used
- Display key extracted information
- Show workflow that was triggered
- Report where results were saved
- Provide next steps if any action is required

## Key Benefits:
- **One Tool for Everything**: No need to know document type beforehand
- **Smart Classification**: Automatically detects invoice, brokerage, DMV, legal, medical, tax, or general documents
- **Intelligent Routing**: Uses specialized extractors for invoices/brokerage, general extraction for others
- **Full Automation**: Workflows trigger automatically based on content (DMV → urgent tasks, invoices → QuickBooks matching)
- **Organized Storage**: Results saved to appropriate folders (/output/invoices/, /output/brokerage/, /output/general/)
- **CRM Integration**: Communications and tasks created automatically

## Example Use Cases:
- DMV notices → Creates urgent tasks and links to DMV company
- Healthcare invoices → Processes through invoice workflow + QuickBooks integration
- Brokerage statements → Financial analysis and review tasks
- Legal documents → Legal notice processing workflow
- Medical records → Medical document processing workflow
- Tax documents → Tax document processing workflow
- Any other document → General extraction with key information

This is the main universal workflow for processing ANY document type with full intelligence and automation.