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
        
        # 🚀 AUTO-TRIGGER WORKFLOWS
        trigger_workflow_automation(result, "invoice")
        
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
        
        # 🚀 AUTO-TRIGGER WORKFLOWS
        trigger_workflow_automation(result, "brokerage")
        
        return result
        
    except Exception as error:
        logger.error(f"Error extracting structured brokerage data: {error}")
        raise Exception(f"Failed to extract structured brokerage data: {str(error)}")

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
- 'extractInvoiceData': Extract both raw text AND structured invoice data in one operation
- 'extractbrokerage': Extract both raw text AND structured brokerage statement data in one operation

Output files are saved to: 
- Invoices: /Users/andrew/Projects/claudecode1/output/invoices/
- Brokerage: /Users/andrew/Projects/claudecode1/output/brokerage/
"""

if __name__ == "__main__":
    logger.info("Starting Vision MCP server...")
    mcp.run()