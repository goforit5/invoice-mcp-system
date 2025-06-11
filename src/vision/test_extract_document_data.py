#!/usr/bin/env python3
"""
Test the new extractDocumentData universal document processor
Demonstrates automatic routing to specialized extractors and workflow automation
"""

import json
from pathlib import Path

def test_document_classification_logic():
    """Test the document classification logic with various text samples"""
    
    print("🧪 Testing Document Classification Logic")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Invoice Document",
            "text": "INVOICE #12345 Payment Due: $500.00 Bill To: John Doe Total Amount: $500.00",
            "expected": "invoice"
        },
        {
            "name": "Brokerage Statement",
            "text": "Fidelity Investments Quarterly Statement Portfolio Value: $50,000 Investment Holdings",
            "expected": "brokerage"
        },
        {
            "name": "DMV Notice",
            "text": "Department of Motor Vehicles Notice of Intent to Suspend Vehicle Registration License Plate: ABC123",
            "expected": "dmv"
        },
        {
            "name": "Legal Document",
            "text": "Superior Court of California Summons Case Number: CV-2025-001 You are hereby summoned",
            "expected": "legal"
        },
        {
            "name": "Medical Record",
            "text": "Stanford Medical Center Patient: John Doe Doctor: Dr. Smith Diagnosis: Annual Checkup",
            "expected": "medical"
        },
        {
            "name": "Tax Document",
            "text": "Form 1099-INT Interest Income IRS Department of Treasury Tax Year 2024",
            "expected": "tax"
        },
        {
            "name": "General Document",
            "text": "Meeting notes from today's discussion about project updates and next steps",
            "expected": "general"
        }
    ]
    
    # Import the classification function
    import sys
    sys.path.append(str(Path(__file__).parent))
    from server import classify_document_simple
    
    for test in test_cases:
        result = classify_document_simple(test["text"], "test.pdf")
        status = "✅" if result == test["expected"] else "❌"
        print(f"{status} {test['name']}: Expected '{test['expected']}', Got '{result}'")
    
    print()

def demonstrate_usage():
    """Show how to use the new extractDocumentData tool"""
    
    print("📋 How to Use extractDocumentData")
    print("=" * 50)
    print()
    
    print("🎯 **Basic Usage:**")
    print("```python")
    print("# Process ANY document - system automatically handles everything")
    print("result = mcp__vision__extractDocumentData('test-documents/any-document.pdf')")
    print("```")
    print()
    
    print("📊 **What You Get Back:**")
    print("```json")
    sample_result = {
        "filename": "document.pdf",
        "document_type": "invoice",  # Automatically classified
        "total_pages": 2,
        "processing_time": "15.3s",
        "extracted_text": ["...full text..."],
        "classification": {
            "document_type": "invoice",
            "extractor_used": "invoice",  # Which specialized extractor was used
            "confidence": 0.95
        },
        "structured_data": {
            # Invoice-specific structured data (if invoice)
            # Brokerage-specific data (if brokerage)
            # General document data (if other)
        },
        "output_file": "/output/invoices/document_2025-06-09_invoice.json",
        "workflow_triggered": True,
        "workflow_type": "Invoice Processing"
    }
    print(json.dumps(sample_result, indent=2))
    print("```")
    print()

def show_document_flow():
    """Show the processing flow for different document types"""
    
    print("🔄 Document Processing Flow")
    print("=" * 50)
    print()
    
    flows = [
        {
            "type": "Invoice",
            "flow": [
                "1. Extract text from PDF",
                "2. Detect invoice keywords",
                "3. Route to invoice extractor",
                "4. Extract vendor, amounts, dates",
                "5. Save to /output/invoices/",
                "6. Trigger Invoice Processing workflow",
                "7. → QuickBooks vendor matching",
                "8. → Create approval task"
            ]
        },
        {
            "type": "DMV Notice",
            "flow": [
                "1. Extract text from PDF",
                "2. Detect DMV/vehicle keywords",
                "3. Use general extractor",
                "4. Extract dates, amounts, deadlines",
                "5. Save to /output/general/",
                "6. Trigger DMV Document Processing workflow",
                "7. → Create urgent task",
                "8. → Link to DMV company"
            ]
        },
        {
            "type": "Brokerage Statement",
            "flow": [
                "1. Extract text from PDF",
                "2. Detect investment keywords",
                "3. Route to brokerage extractor",
                "4. Extract holdings, transactions",
                "5. Save to /output/brokerage/",
                "6. Trigger Financial Statement Processing workflow",
                "7. → Create review task",
                "8. → Log transactions"
            ]
        }
    ]
    
    for doc_flow in flows:
        print(f"📄 **{doc_flow['type']} Document:**")
        for step in doc_flow['flow']:
            print(f"   {step}")
        print()

def show_example_commands():
    """Show example commands for different document types"""
    
    print("💡 Example Commands")
    print("=" * 50)
    print()
    
    examples = [
        {
            "file": "Document_20250221_0001.pdf",
            "description": "DMV suspension notice"
        },
        {
            "file": "Clipboard_236823VP.pdf",
            "description": "Healthcare invoice"
        },
        {
            "file": "Fidelity_Investments_Statement_July_2019.pdf",
            "description": "Brokerage statement"
        },
        {
            "file": "court_summons_2025.pdf",
            "description": "Legal document"
        },
        {
            "file": "medical_report.pdf",
            "description": "Medical record"
        },
        {
            "file": "random_document.pdf",
            "description": "Unknown document type"
        }
    ]
    
    print("# Process various document types:")
    for ex in examples:
        print(f"# {ex['description']}")
        print(f"mcp__vision__extractDocumentData('test-documents/{ex['file']}')")
        print()

def show_benefits():
    """Show the benefits of the new approach"""
    
    print("✨ Benefits of extractDocumentData")
    print("=" * 50)
    print()
    
    benefits = [
        "🎯 **One Tool for Everything**: No need to know document type beforehand",
        "🤖 **Smart Routing**: Automatically uses best extractor (invoice/brokerage/general)",
        "⚡ **Full Automation**: Workflows trigger automatically based on content",
        "📊 **Unified Output**: Consistent result format regardless of document type",
        "🔄 **Backward Compatible**: Old tools still work if needed",
        "📈 **Scalable**: Easy to add new document types and extractors"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    print()

if __name__ == "__main__":
    print("🚀 extractDocumentData - Universal Document Processor")
    print("=" * 60)
    print()
    
    # Run all demonstrations
    test_document_classification_logic()
    demonstrate_usage()
    show_document_flow()
    show_example_commands()
    show_benefits()
    
    print("🎉 **Summary:**")
    print("=" * 30)
    print("Use `mcp__vision__extractDocumentData()` for ALL documents!")
    print("The system will:")
    print("  1. Classify the document type")
    print("  2. Route to the best extractor")
    print("  3. Extract structured data")
    print("  4. Trigger appropriate workflows")
    print("  5. Save results to organized folders")
    print("\nZERO manual intervention required! 🚀")