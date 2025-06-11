#!/Users/andrew/Projects/claudecode1/vision-mcp-env/bin/python3
"""
MCP server for vision functionality - PDF text extraction using OpenAI Vision API
"""

import asyncio
import logging
import requests
import json
from mcp.server.fastmcp import FastMCP
from index import extract_pdf_text, extract_structured_invoice_data, save_invoice_json, extract_structured_brokerage_data, save_brokerage_json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Vision MCP")

# Workflow automation configuration
WORKFLOW_TRIGGER_ENABLED = True
CRM_SERVER_URL = "http://localhost:3002"  # CRM MCP server URL
WORKFLOW_SERVER_URL = "http://localhost:3003"  # Workflow MCP server URL

def trigger_workflow_automation(extracted_data: dict, document_type: str = "invoice"):
    """
    Automatically trigger workflows based on extracted document data
    """
    if not WORKFLOW_TRIGGER_ENABLED:
        return
    
    try:
        logger.info(f"🚀 Auto-triggering workflows for {document_type} document")
        
        # Determine document classification and appropriate workflow
        workflow_mapping = classify_document_and_get_workflow(extracted_data)
        
        if workflow_mapping:
            # Create communication record in CRM with auto-workflow trigger
            create_communication_with_workflow(extracted_data, workflow_mapping)
        
    except Exception as e:
        logger.error(f"Failed to trigger workflow automation: {e}")

def classify_document_and_get_workflow(extracted_data: dict) -> dict:
    """
    Classify the document and determine which workflow to trigger
    """
    text_content = ""
    filename = extracted_data.get("filename", "")
    
    # Get text content from various extraction formats
    if "extracted_text" in extracted_data:
        for page in extracted_data["extracted_text"]:
            text_content += page.get("text", "") + " "
    
    text_lower = text_content.lower()
    filename_lower = filename.lower()
    
    # DMV Documents
    if any(keyword in text_lower for keyword in ["motor vehicles", "dmv", "suspend", "registration"]):
        return {
            "workflow_name": "DMV Document Processing",
            "sender_identifier": "dmv.ca.gov",
            "sender_name": "California Department of Motor Vehicles",
            "platform": "mail",
            "subject": extract_dmv_subject(text_content),
            "category": "government_notice"
        }
    
    # Invoice Documents  
    elif any(keyword in text_lower for keyword in ["invoice", "bill", "payment", "due date"]):
        return {
            "workflow_name": "Invoice Processing",
            "sender_identifier": extract_invoice_sender(text_content),
            "sender_name": extract_invoice_company(text_content),
            "platform": "mail", 
            "subject": f"Invoice - {filename}",
            "category": "invoice"
        }
    
    # Legal Documents
    elif any(keyword in text_lower for keyword in ["notice", "legal", "court", "summons"]):
        return {
            "workflow_name": "Legal Notice Processing",
            "sender_identifier": extract_legal_sender(text_content),
            "sender_name": extract_legal_entity(text_content),
            "platform": "mail",
            "subject": f"Legal Notice - {filename}",
            "category": "legal_notice"
        }
    
    # Medical Documents
    elif any(keyword in text_lower for keyword in ["medical", "health", "patient", "doctor"]):
        return {
            "workflow_name": "Medical Document Processing",
            "sender_identifier": extract_medical_sender(text_content),
            "sender_name": extract_medical_facility(text_content),
            "platform": "mail",
            "subject": f"Medical Document - {filename}",
            "category": "medical"
        }
    
    # Financial Statements
    elif any(keyword in text_lower for keyword in ["statement", "brokerage", "investment", "portfolio"]):
        return {
            "workflow_name": "Financial Statement Processing",
            "sender_identifier": extract_financial_sender(text_content),
            "sender_name": extract_financial_institution(text_content),
            "platform": "mail",
            "subject": f"Financial Statement - {filename}",
            "category": "financial"
        }
    
    # Default fallback
    else:
        return {
            "workflow_name": "General Document Processing",
            "sender_identifier": "unknown@document.com",
            "sender_name": "Unknown Sender",
            "platform": "document",
            "subject": f"Document - {filename}",
            "category": "general"
        }

def extract_dmv_subject(text: str) -> str:
    """Extract subject line for DMV documents"""
    if "suspend" in text.lower():
        license_match = None
        for line in text.split('\n'):
            if "license" in line.lower() and any(char.isdigit() for char in line):
                license_match = line.strip()
                break
        return f"Notice of Intent to Suspend - {license_match if license_match else 'Vehicle Registration'}"
    return "DMV Notice"

def extract_invoice_sender(text: str) -> str:
    """Extract sender email/identifier from invoice"""
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if "@" in line and any(domain in line for domain in [".com", ".org", ".net"]):
            return line.strip()
    return "invoice@company.com"

def extract_invoice_company(text: str) -> str:
    """Extract company name from invoice"""
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines for company name
        if line.strip() and not any(char.isdigit() for char in line) and len(line.strip()) > 5:
            return line.strip()
    return "Invoice Company"

def extract_legal_sender(text: str) -> str:
    """Extract sender for legal documents"""
    if "court" in text.lower():
        return "court@legal.gov"
    return "legal@lawfirm.com"

def extract_legal_entity(text: str) -> str:
    """Extract legal entity name"""
    if "court" in text.lower():
        return "Superior Court"
    return "Legal Entity"

def extract_medical_sender(text: str) -> str:
    """Extract medical facility identifier"""
    return "records@medical.com"

def extract_medical_facility(text: str) -> str:
    """Extract medical facility name"""
    lines = text.split('\n')
    for line in lines[:5]:
        if any(keyword in line.lower() for keyword in ["medical", "health", "clinic", "hospital"]):
            return line.strip()
    return "Medical Facility"

def extract_financial_sender(text: str) -> str:
    """Extract financial institution identifier"""
    if "fidelity" in text.lower():
        return "statements@fidelity.com"
    elif "schwab" in text.lower():
        return "statements@schwab.com"
    return "statements@financial.com"

def extract_financial_institution(text: str) -> str:
    """Extract financial institution name"""
    text_lower = text.lower()
    if "fidelity" in text_lower:
        return "Fidelity Investments"
    elif "schwab" in text_lower:
        return "Charles Schwab"
    elif "vanguard" in text_lower:
        return "Vanguard"
    return "Financial Institution"

def create_communication_with_workflow(extracted_data: dict, workflow_mapping: dict):
    """
    Create communication record in CRM and trigger appropriate workflow
    """
    try:
        # Prepare text content
        text_content = ""
        if "extracted_text" in extracted_data:
            for page in extracted_data["extracted_text"]:
                text_content += page.get("text", "") + "\n\n"
        
        # Create communication data
        communication_data = {
            "platform": workflow_mapping["platform"],
            "sender_identifier": workflow_mapping["sender_identifier"],
            "content": text_content,
            "subject": workflow_mapping["subject"],
            "direction": "incoming",
            "sender_name": workflow_mapping["sender_name"],
            "auto_trigger_workflows": True
        }
        
        logger.info(f"📧 Creating communication record for {workflow_mapping['workflow_name']}")
        
        # In production, this would make HTTP call to CRM server
        # For now, we'll log the trigger and create a mock communication
        mock_communication = {
            "id": 999,  # Mock ID
            "platform": communication_data["platform"],
            "sender_identifier": communication_data["sender_identifier"],
            "message_content_text": communication_data["content"],
            "subject_line": communication_data["subject"],
            "sender_display_name": communication_data["sender_name"],
            "direction": "incoming",
            "communication_timestamp": "2025-06-09T17:45:00",
            "content_category": workflow_mapping["category"]
        }
        
        # Trigger the specific workflow
        trigger_specific_workflow(workflow_mapping["workflow_name"], mock_communication)
        
        logger.info(f"✅ Successfully triggered {workflow_mapping['workflow_name']} workflow")
        
    except Exception as e:
        logger.error(f"Failed to create communication with workflow: {e}")

def trigger_specific_workflow(workflow_name: str, communication_data: dict):
    """
    Trigger a specific workflow with communication data
    """
    try:
        logger.info(f"🔄 Triggering workflow: {workflow_name}")
        
        # In production, this would call the Workflow MCP server via HTTP
        # For demonstration, we'll simulate the trigger
        
        workflow_trigger_data = {
            "workflow_name": workflow_name,
            "trigger_event": "document.processed",
            "trigger_data": communication_data
        }
        
        logger.info(f"📊 Workflow trigger data: {json.dumps(workflow_trigger_data, indent=2)}")
        
        # This would normally be:
        # response = requests.post(f"{WORKFLOW_SERVER_URL}/trigger", json=workflow_trigger_data)
        
        return {"success": True, "workflow_triggered": workflow_name}
        
    except Exception as e:
        logger.error(f"Failed to trigger workflow {workflow_name}: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def extractInvoiceData(file_path: str) -> dict:
    """
    Extract structured invoice data from PDF and save as JSON
    
    Args:
        file_path: Path to PDF file in /Users/andrew/Projects/claudecode1/test-documents
    
    Returns:
        JSON object with extraction results and path to saved structured data file
    """
    try:
        logger.info(f"Extracting structured invoice data from: {file_path}")
        
        # Validate file path is in allowed directory
        allowed_dir = "/Users/andrew/Projects/claudecode1/test-documents"
        if not file_path.startswith(allowed_dir):
            raise ValueError(f"File must be in {allowed_dir}")
        
        # First extract text using OpenAI Vision
        text_result = extract_pdf_text(file_path)
        
        # Combine all page text
        combined_text = ""
        for page_data in text_result["extracted_text"]:
            combined_text += page_data["text"] + "\n\n"
        
        # Extract structured data
        structured_result = extract_structured_invoice_data(combined_text, text_result["filename"])
        
        # Save structured data to JSON file
        output_file = save_invoice_json(structured_result["structured_data"], text_result["filename"])
        
        # Combine costs
        total_extraction_cost = text_result["total_cost_summary"]["total_cost"]
        structured_cost = structured_result["extraction_cost"]["total_cost"]
        total_cost = total_extraction_cost + structured_cost
        
        result = {
            "filename": text_result["filename"],
            "total_pages": text_result["total_pages"],
            "processing_time": text_result["processing_time"],
            "extracted_text": text_result["extracted_text"],
            "structured_data": structured_result["structured_data"],
            "output_file": output_file,
            "cost_breakdown": {
                "text_extraction_cost": total_extraction_cost,
                "structured_extraction_cost": structured_cost,
                "total_cost": round(total_cost, 6)
            }
        }
        
        logger.info(f"Successfully extracted and saved structured invoice data to: {output_file}")
        
        # NOTE: Workflow triggers removed - use extractDocumentData for automation
        
        return result
        
    except Exception as error:
        logger.error(f"Error extracting structured invoice data: {error}")
        raise Exception(f"Failed to extract structured invoice data: {str(error)}")

@mcp.tool()
def extractbrokerage(file_path: str) -> dict:
    """
    Extract structured brokerage statement data from PDF and save as JSON
    
    Args:
        file_path: Path to PDF file in /Users/andrew/Projects/claudecode1/test-documents
    
    Returns:
        JSON object with extraction results and path to saved structured data file
    """
    try:
        logger.info(f"Extracting structured brokerage data from: {file_path}")
        
        # Validate file path is in allowed directory
        allowed_dir = "/Users/andrew/Projects/claudecode1/test-documents"
        if not file_path.startswith(allowed_dir):
            raise ValueError(f"File must be in {allowed_dir}")
        
        # First extract text using OpenAI Vision
        text_result = extract_pdf_text(file_path)
        
        # Combine all page text
        combined_text = ""
        for page_data in text_result["extracted_text"]:
            combined_text += page_data["text"] + "\n\n"
        
        # Extract structured data
        structured_result = extract_structured_brokerage_data(combined_text, text_result["filename"])
        
        # Save structured data to JSON file
        output_file = save_brokerage_json(structured_result["structured_data"], text_result["filename"])
        
        # Combine costs
        total_extraction_cost = text_result["total_cost_summary"]["total_cost"]
        structured_cost = structured_result["extraction_cost"]["total_cost"]
        total_cost = total_extraction_cost + structured_cost
        
        result = {
            "filename": text_result["filename"],
            "total_pages": text_result["total_pages"],
            "processing_time": text_result["processing_time"],
            "extracted_text": text_result["extracted_text"],
            "structured_data": structured_result["structured_data"],
            "output_file": output_file,
            "cost_breakdown": {
                "text_extraction_cost": total_extraction_cost,
                "structured_extraction_cost": structured_cost,
                "total_cost": round(total_cost, 6)
            }
        }
        
        logger.info(f"Successfully extracted and saved structured brokerage data to: {output_file}")
        
        # NOTE: Workflow triggers removed - use extractDocumentData for automation
        
        return result
        
    except Exception as error:
        logger.error(f"Error extracting structured brokerage data: {error}")
        raise Exception(f"Failed to extract structured brokerage data: {str(error)}")

@mcp.tool()
def extractDocumentData(file_path: str) -> dict:
    """
    Universal document processor - extracts data from any PDF and routes to specialized extractors as needed
    
    Args:
        file_path: Path to PDF file in /Users/andrew/Projects/claudecode1/test-documents
    
    Returns:
        JSON object with extraction results, document classification, and workflow automation status
    """
    try:
        logger.info(f"🔍 Processing document with universal extractor: {file_path}")
        
        # Validate file path is in allowed directory
        allowed_dir = "/Users/andrew/Projects/claudecode1/test-documents"
        if not file_path.startswith(allowed_dir):
            raise ValueError(f"File must be in {allowed_dir}")
        
        # Step 1: Extract text using OpenAI Vision (common for all documents)
        logger.info("📄 Step 1: Extracting text from PDF...")
        text_result = extract_pdf_text(file_path)
        
        # Combine all page text for classification
        combined_text = ""
        for page_data in text_result["extracted_text"]:
            combined_text += page_data["text"] + "\n\n"
        
        # Step 2: Classify document type
        logger.info("🎯 Step 2: Classifying document type...")
        doc_type = classify_document_simple(combined_text, text_result["filename"])
        logger.info(f"   Document classified as: {doc_type}")
        
        # Step 3: Route to appropriate extractor
        logger.info("🔀 Step 3: Routing to specialized extractor if applicable...")
        structured_data = None
        specialized_result = None
        
        if doc_type == "invoice":
            logger.info("   → Using specialized invoice extractor")
            # Extract structured invoice data
            structured_result = extract_structured_invoice_data(combined_text, text_result["filename"])
            specialized_result = {
                "extractor_used": "invoice",
                "structured_data": structured_result["structured_data"],
                "output_file": save_invoice_json(structured_result["structured_data"], text_result["filename"])
            }
            
        elif doc_type == "brokerage":
            logger.info("   → Using specialized brokerage extractor")
            # Extract structured brokerage data
            structured_result = extract_structured_brokerage_data(combined_text, text_result["filename"])
            specialized_result = {
                "extractor_used": "brokerage",
                "structured_data": structured_result["structured_data"],
                "output_file": save_brokerage_json(structured_result["structured_data"], text_result["filename"])
            }
            
        else:
            logger.info("   → Using general document extraction")
            # Extract general document data
            structured_data = extract_general_document_data(combined_text, text_result["filename"])
            specialized_result = {
                "extractor_used": "general",
                "structured_data": structured_data,
                "output_file": save_general_json(structured_data, text_result["filename"])
            }
        
        # Step 4: Trigger workflow automation
        logger.info("⚡ Step 4: Triggering workflow automation...")
        
        # Prepare unified result
        result = {
            "filename": text_result["filename"],
            "document_type": doc_type,
            "total_pages": text_result["total_pages"],
            "processing_time": text_result["processing_time"],
            "extracted_text": text_result["extracted_text"],
            "classification": {
                "document_type": doc_type,
                "extractor_used": specialized_result["extractor_used"],
                "confidence": 0.95  # Placeholder - can enhance with real confidence scoring
            },
            "structured_data": specialized_result["structured_data"],
            "output_file": specialized_result["output_file"],
            "cost_breakdown": text_result.get("total_cost_summary", {})
        }
        
        # Trigger workflow automation with document type
        trigger_workflow_automation(result, doc_type)
        
        # Add workflow status to result
        result["workflow_triggered"] = True
        result["workflow_type"] = get_workflow_for_document_type(doc_type)
        
        logger.info(f"✅ Successfully processed document: {file_path}")
        logger.info(f"   Document Type: {doc_type}")
        logger.info(f"   Extractor Used: {specialized_result['extractor_used']}")
        logger.info(f"   Output File: {specialized_result['output_file']}")
        logger.info(f"   Workflow Triggered: {result['workflow_type']}")
        
        return result
        
    except Exception as error:
        logger.error(f"Error processing document: {error}")
        raise Exception(f"Failed to process document: {str(error)}")

def classify_document_simple(text_content: str, filename: str) -> str:
    """
    Simple document classification based on keywords
    
    Returns: invoice, brokerage, dmv, legal, medical, tax, or general
    """
    text_lower = text_content.lower()
    filename_lower = filename.lower()
    
    # Check for invoice indicators
    invoice_keywords = ["invoice", "bill", "payment due", "amount due", "total amount", "remit to", "payment terms"]
    if any(keyword in text_lower for keyword in invoice_keywords):
        return "invoice"
    
    # Check for brokerage/financial statement indicators
    brokerage_keywords = ["brokerage", "statement", "portfolio", "investment", "securities", "holdings", "account value", "fidelity", "schwab", "vanguard"]
    if any(keyword in text_lower for keyword in brokerage_keywords):
        return "brokerage"
    
    # Check for DMV/government indicators
    dmv_keywords = ["motor vehicles", "dmv", "vehicle registration", "license plate", "suspend"]
    if any(keyword in text_lower for keyword in dmv_keywords):
        return "dmv"
    
    # Check for legal document indicators
    legal_keywords = ["court", "legal notice", "summons", "lawsuit", "attorney", "case number"]
    if any(keyword in text_lower for keyword in legal_keywords):
        return "legal"
    
    # Check for medical document indicators
    medical_keywords = ["medical", "patient", "doctor", "clinic", "hospital", "diagnosis", "treatment"]
    if any(keyword in text_lower for keyword in medical_keywords):
        return "medical"
    
    # Check for tax document indicators
    tax_keywords = ["tax", "1099", "w-2", "w2", "irs", "internal revenue", "tax return"]
    if any(keyword in text_lower for keyword in tax_keywords):
        return "tax"
    
    # Default to general document
    return "general"

def extract_general_document_data(text_content: str, filename: str) -> dict:
    """
    Extract general document data when no specialized extractor applies
    """
    import re
    
    # Extract dates
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    dates = re.findall(date_pattern, text_content)
    
    # Extract amounts
    amount_pattern = r'\$[\d,]+\.?\d*'
    amounts = re.findall(amount_pattern, text_content)
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text_content)
    
    # Extract phone numbers
    phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phones = re.findall(phone_pattern, text_content)
    
    # Get first few lines as potential title/header
    lines = text_content.split('\n')
    title_candidates = [line.strip() for line in lines[:5] if line.strip() and len(line.strip()) > 5]
    
    # Create general document structure
    general_doc = {
        "document_metadata": {
            "document_type": "general",
            "document_date": dates[0] if dates else None,
            "document_title": title_candidates[0] if title_candidates else filename,
            "sender_organization": "Unknown",
            "recipient_name": "Unknown"
        },
        "key_information": {
            "dates": dates[:5],  # Limit to first 5 dates
            "amounts": amounts[:5],  # Limit to first 5 amounts
            "reference_numbers": [],
            "names": [],
            "addresses": emails[:3]  # Use emails as addresses
        },
        "action_items": {
            "required_actions": [],
            "deadlines": [],
            "urgency_level": "medium"
        },
        "document_summary": {
            "main_purpose": f"General document: {filename}",
            "key_points": [
                f"Document contains {len(dates)} dates",
                f"Document contains {len(amounts)} monetary amounts",
                f"Document length: {len(text_content)} characters"
            ],
            "category": "general"
        },
        "technical_details": {
            "total_pages": 1,  # Will be updated from actual page count
            "language": "english",
            "quality_score": 90
        }
    }
    
    return general_doc

def save_general_json(data: dict, filename: str) -> str:
    """
    Save general document data to JSON file
    """
    import json
    from pathlib import Path
    from datetime import datetime
    
    # Create output directory if it doesn't exist
    output_dir = Path("/Users/andrew/Projects/claudecode1/output/general")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    base_name = Path(filename).stem
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"{base_name}_{timestamp}_general.json"
    output_path = output_dir / output_filename
    
    # Save to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(output_path)

def get_workflow_for_document_type(doc_type: str) -> str:
    """
    Map document type to workflow name
    """
    workflow_mapping = {
        "invoice": "Invoice Processing",
        "brokerage": "Financial Statement Processing",
        "dmv": "DMV Document Processing",
        "legal": "Legal Notice Processing",
        "medical": "Medical Document Processing",
        "tax": "Tax Document Processing",
        "general": "General Document Processing"
    }
    
    return workflow_mapping.get(doc_type, "General Document Processing")

@mcp.resource("vision://about")
def get_about() -> str:
    """Information about the Vision MCP server"""
    return """
Vision MCP Server
-----------------
A PDF text extraction service that enables:
- Converting PDF pages to images
- Using OpenAI Vision API for text extraction
- Returning structured JSON with text per page
- Processing files from test-documents directory
- Extracting structured invoice data using templates
- Saving structured data as JSON files

Available tools:
- 'extractDocumentData': Universal document processor - automatically routes to specialized extractors
- 'extractInvoiceData': Extract both raw text AND structured invoice data (specialized)
- 'extractbrokerage': Extract both raw text AND structured brokerage statement data (specialized)

Output files are saved to: 
- Invoices: /Users/andrew/Projects/claudecode1/output/invoices/
- Brokerage: /Users/andrew/Projects/claudecode1/output/brokerage/
- General: /Users/andrew/Projects/claudecode1/output/general/
"""

if __name__ == "__main__":
    logger.info("Starting Vision MCP server...")
    mcp.run()