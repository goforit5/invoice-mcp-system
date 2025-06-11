"""
Integration module for connecting QuickBooks MCP with Vision MCP
Handles end-to-end invoice processing workflow
"""

import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def call_vision_mcp(file_path: str) -> Dict:
    """
    Call the Vision MCP server to extract invoice data
    This would typically use MCP client calls, but for now we'll simulate
    """
    try:
        # In a real implementation, this would make an MCP call to the vision server
        # For now, we'll simulate the call
        logger.info(f"Calling Vision MCP to extract data from: {file_path}")
        
        # Simulate vision extraction result
        # In reality, this would be: vision_client.call_tool("extractInvoiceData", {"file_path": file_path})
        return {
            "filename": Path(file_path).name,
            "structured_data": {
                "vendor_name": "Acme Supplies Inc.",
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15",
                "due_date": "2024-02-14",
                "total_amount": 1250.75,
                "line_items": [
                    {
                        "description": "Office supplies",
                        "quantity": 10,
                        "unit_price": 25.50,
                        "amount": 255.00
                    },
                    {
                        "description": "Software subscription",
                        "quantity": 1,
                        "unit_price": 995.75,
                        "amount": 995.75
                    }
                ]
            },
            "output_file": "/path/to/structured/data.json"
        }
        
    except Exception as e:
        logger.error(f"Error calling Vision MCP: {e}")
        raise Exception(f"Failed to extract invoice data: {str(e)}")

def process_invoice_complete(file_path: str, auto_post: bool = False) -> Dict:
    """
    Complete end-to-end invoice processing workflow
    """
    try:
        from index import match_vendor, create_vendor, get_vendor_history, auto_code_invoice, post_to_quickbooks
        
        results = {
            "file_path": file_path,
            "steps_completed": [],
            "final_status": "processing"
        }
        
        # Step 1: Extract invoice data using Vision MCP
        logger.info("Step 1: Extracting invoice data...")
        vision_result = call_vision_mcp(file_path)
        invoice_data = vision_result["structured_data"]
        results["steps_completed"].append("data_extraction")
        results["extracted_data"] = invoice_data
        
        # Step 2: Match vendor
        logger.info("Step 2: Matching vendor...")
        vendor_match = match_vendor(invoice_data)
        results["steps_completed"].append("vendor_matching")
        results["vendor_match"] = vendor_match
        
        vendor_id = None
        if vendor_match["status"] == "exact_match":
            vendor_id = vendor_match["vendor"]["Id"]
            logger.info(f"Found exact vendor match: {vendor_match['vendor']['DisplayName']}")
        elif vendor_match["status"] == "partial_matches":
            # Use first partial match for now
            vendor_id = vendor_match["matches"][0]["Id"]
            logger.info(f"Using partial vendor match: {vendor_match['matches'][0]['DisplayName']}")
        elif vendor_match["status"] == "no_match":
            # Create new vendor
            logger.info("Creating new vendor...")
            new_vendor = create_vendor(vendor_match["suggestion"])
            vendor_id = new_vendor["Id"]
            results["steps_completed"].append("vendor_creation")
            results["new_vendor"] = new_vendor
        
        # Step 3: Get vendor history for coding patterns
        logger.info("Step 3: Analyzing vendor history...")
        if vendor_id:
            vendor_history = get_vendor_history(vendor_id)
            results["steps_completed"].append("history_analysis")
            results["vendor_history"] = vendor_history
        
        # Step 4: Auto-code the invoice
        logger.info("Step 4: Auto-coding invoice...")
        coded_invoice = auto_code_invoice(invoice_data, vendor_id)
        results["steps_completed"].append("invoice_coding")
        results["coded_invoice"] = coded_invoice
        
        # Step 5: Post to QuickBooks (if auto_post or high confidence)
        avg_confidence = coded_invoice.get("coding_confidence", 0)
        if auto_post or avg_confidence > 0.8:
            logger.info("Step 5: Posting to QuickBooks...")
            post_result = post_to_quickbooks(coded_invoice, auto_post=True)
            results["steps_completed"].append("quickbooks_posting")
            results["post_result"] = post_result
            
            if post_result["status"] == "posted":
                results["final_status"] = "completed"
                results["bill_id"] = post_result["bill_id"]
            else:
                results["final_status"] = "posted_with_issues"
        else:
            logger.info("Step 5: Coding confidence too low, requiring manual review...")
            results["final_status"] = "requires_review"
            results["review_reason"] = f"Coding confidence {avg_confidence:.2f} below threshold"
        
        # Summary
        results["summary"] = {
            "vendor": vendor_match.get("vendor", {}).get("DisplayName", "New Vendor"),
            "total_amount": invoice_data.get("total_amount", 0),
            "line_items_count": len(invoice_data.get("line_items", [])),
            "processing_time": "simulated",
            "confidence_score": avg_confidence
        }
        
        logger.info(f"End-to-end processing completed with status: {results['final_status']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in end-to-end processing: {e}")
        results["final_status"] = "failed"
        results["error"] = str(e)
        return results

def setup_mcp_integration():
    """
    Set up integration between QuickBooks and Vision MCP servers
    This would configure the MCP client connections
    """
    logger.info("Setting up MCP server integration...")
    
    # In a real implementation, this would:
    # 1. Initialize MCP client for Vision server
    # 2. Test connectivity
    # 3. Set up any required authentication
    
    return {
        "vision_mcp_connected": True,
        "quickbooks_mcp_ready": True,
        "integration_status": "configured"
    }