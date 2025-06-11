#!/Users/andrew/Projects/claudecode1/vision-mcp-env/bin/python3
"""
MCP server for QuickBooks functionality - Full invoice processing automation
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from index import (
    authenticate_quickbooks, get_vendors, create_vendor, update_vendor,
    get_bills, create_bill, update_bill, get_chart_of_accounts,
    match_vendor, get_vendor_history, auto_code_invoice, post_to_quickbooks
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("QuickBooks MCP")

@mcp.tool()
def authenticate(client_id: str, client_secret: str, redirect_uri: str, environment: str = "sandbox") -> dict:
    """
    Authenticate with QuickBooks and save credentials for future use
    
    Args:
        client_id: QuickBooks app client ID
        client_secret: QuickBooks app client secret  
        redirect_uri: QuickBooks app redirect URI
        environment: 'sandbox' or 'production'
    
    Returns:
        Authentication status and instructions
    """
    try:
        logger.info("Starting QuickBooks authentication...")
        result = authenticate_quickbooks(client_id, client_secret, redirect_uri, environment)
        logger.info("QuickBooks authentication completed")
        return result
    except Exception as error:
        logger.error(f"Error authenticating with QuickBooks: {error}")
        raise Exception(f"Failed to authenticate: {str(error)}")

@mcp.tool()
def listVendors(active_only: bool = True) -> dict:
    """
    Get all vendors from QuickBooks
    
    Args:
        active_only: Only return active vendors
    
    Returns:
        List of vendors with their details
    """
    try:
        logger.info("Fetching vendors from QuickBooks...")
        vendors = get_vendors(active_only)
        logger.info(f"Retrieved {len(vendors)} vendors")
        return {"vendors": vendors, "count": len(vendors)}
    except Exception as error:
        logger.error(f"Error fetching vendors: {error}")
        raise Exception(f"Failed to fetch vendors: {str(error)}")

@mcp.tool()
def createVendor(vendor_data: dict) -> dict:
    """
    Create a new vendor in QuickBooks
    
    Args:
        vendor_data: Dictionary with vendor information (DisplayName required)
    
    Returns:
        Created vendor details
    """
    try:
        logger.info(f"Creating vendor: {vendor_data.get('DisplayName', 'Unknown')}")
        vendor = create_vendor(vendor_data)
        logger.info(f"Successfully created vendor with ID: {vendor.get('Id')}")
        return vendor
    except Exception as error:
        logger.error(f"Error creating vendor: {error}")
        raise Exception(f"Failed to create vendor: {str(error)}")

@mcp.tool()
def updateVendor(vendor_id: str, vendor_data: dict) -> dict:
    """
    Update an existing vendor in QuickBooks
    
    Args:
        vendor_id: QuickBooks vendor ID
        vendor_data: Dictionary with updated vendor information
    
    Returns:
        Updated vendor details
    """
    try:
        logger.info(f"Updating vendor ID: {vendor_id}")
        vendor = update_vendor(vendor_id, vendor_data)
        logger.info(f"Successfully updated vendor: {vendor.get('DisplayName')}")
        return vendor
    except Exception as error:
        logger.error(f"Error updating vendor: {error}")
        raise Exception(f"Failed to update vendor: {str(error)}")

@mcp.tool()
def listBills(vendor_id: str = None, unpaid_only: bool = False) -> dict:
    """
    Get bills from QuickBooks
    
    Args:
        vendor_id: Optional vendor ID to filter by
        unpaid_only: Only return unpaid bills
    
    Returns:
        List of bills with their details
    """
    try:
        logger.info("Fetching bills from QuickBooks...")
        bills = get_bills(vendor_id, unpaid_only)
        logger.info(f"Retrieved {len(bills)} bills")
        return {"bills": bills, "count": len(bills)}
    except Exception as error:
        logger.error(f"Error fetching bills: {error}")
        raise Exception(f"Failed to fetch bills: {str(error)}")

@mcp.tool()
def createBill(bill_data: dict) -> dict:
    """
    Create a new bill in QuickBooks
    
    Args:
        bill_data: Dictionary with bill information (VendorRef required)
    
    Returns:
        Created bill details
    """
    try:
        logger.info(f"Creating bill for vendor: {bill_data.get('VendorRef', {}).get('value', 'Unknown')}")
        bill = create_bill(bill_data)
        logger.info(f"Successfully created bill with ID: {bill.get('Id')}")
        return bill
    except Exception as error:
        logger.error(f"Error creating bill: {error}")
        raise Exception(f"Failed to create bill: {str(error)}")

@mcp.tool()
def updateBill(bill_id: str, bill_data: dict) -> dict:
    """
    Update an existing bill in QuickBooks
    
    Args:
        bill_id: QuickBooks bill ID
        bill_data: Dictionary with updated bill information
    
    Returns:
        Updated bill details
    """
    try:
        logger.info(f"Updating bill ID: {bill_id}")
        bill = update_bill(bill_id, bill_data)
        logger.info(f"Successfully updated bill")
        return bill
    except Exception as error:
        logger.error(f"Error updating bill: {error}")
        raise Exception(f"Failed to update bill: {str(error)}")

@mcp.tool()
def getChartOfAccounts(active_only: bool = True) -> dict:
    """
    Get chart of accounts from QuickBooks
    
    Args:
        active_only: Only return active accounts
    
    Returns:
        List of accounts with their details
    """
    try:
        logger.info("Fetching chart of accounts from QuickBooks...")
        accounts = get_chart_of_accounts(active_only)
        logger.info(f"Retrieved {len(accounts)} accounts")
        return {"accounts": accounts, "count": len(accounts)}
    except Exception as error:
        logger.error(f"Error fetching chart of accounts: {error}")
        raise Exception(f"Failed to fetch chart of accounts: {str(error)}")

@mcp.tool()
def matchVendorFromInvoice(invoice_data: dict) -> dict:
    """
    Match a vendor from extracted invoice data
    
    Args:
        invoice_data: Structured invoice data from vision extraction
    
    Returns:
        Matched vendor information or suggestion to create new vendor
    """
    try:
        logger.info("Matching vendor from invoice data...")
        result = match_vendor(invoice_data)
        logger.info(f"Vendor matching completed: {result.get('status', 'unknown')}")
        return result
    except Exception as error:
        logger.error(f"Error matching vendor: {error}")
        raise Exception(f"Failed to match vendor: {str(error)}")

@mcp.tool()
def getVendorCodingHistory(vendor_id: str, limit: int = 10) -> dict:
    """
    Get historical coding patterns for a vendor
    
    Args:
        vendor_id: QuickBooks vendor ID
        limit: Number of recent bills to analyze
    
    Returns:
        Historical coding patterns and suggestions
    """
    try:
        logger.info(f"Getting coding history for vendor: {vendor_id}")
        history = get_vendor_history(vendor_id, limit)
        logger.info(f"Retrieved coding history for {len(history.get('bills', []))} bills")
        return history
    except Exception as error:
        logger.error(f"Error getting vendor history: {error}")
        raise Exception(f"Failed to get vendor history: {str(error)}")

@mcp.tool()
def autoCodeInvoice(invoice_data: dict, vendor_id: str = None) -> dict:
    """
    Automatically code invoice line items based on vendor history and chart of accounts
    
    Args:
        invoice_data: Structured invoice data from vision extraction
        vendor_id: Optional vendor ID if already matched
    
    Returns:
        Coded invoice with account assignments for each line item
    """
    try:
        logger.info("Auto-coding invoice line items...")
        coded_invoice = auto_code_invoice(invoice_data, vendor_id)
        logger.info(f"Successfully coded {len(coded_invoice.get('line_items', []))} line items")
        return coded_invoice
    except Exception as error:
        logger.error(f"Error auto-coding invoice: {error}")
        raise Exception(f"Failed to auto-code invoice: {str(error)}")

@mcp.tool()
def postInvoiceToQuickBooks(coded_invoice_data: dict, auto_post: bool = False) -> dict:
    """
    Post coded invoice to QuickBooks as a bill
    
    Args:
        coded_invoice_data: Fully coded invoice with vendor and account assignments
        auto_post: Whether to automatically post without review
    
    Returns:
        Posted bill details and status
    """
    try:
        logger.info("Posting invoice to QuickBooks...")
        result = post_to_quickbooks(coded_invoice_data, auto_post)
        logger.info(f"Successfully posted bill with ID: {result.get('bill_id')}")
        return result
    except Exception as error:
        logger.error(f"Error posting to QuickBooks: {error}")
        raise Exception(f"Failed to post to QuickBooks: {str(error)}")

@mcp.tool()
def processInvoiceEnd2End(invoice_file_path: str, auto_post: bool = False) -> dict:
    """
    Complete end-to-end invoice processing: extract -> match vendor -> code -> post
    
    Args:
        invoice_file_path: Path to PDF invoice file
        auto_post: Whether to automatically post to QuickBooks
    
    Returns:
        Complete processing results including QB bill ID
    """
    try:
        logger.info(f"Starting end-to-end processing for: {invoice_file_path}")
        
        # This would call the vision MCP server to extract invoice data
        # Then process through all the steps automatically
        from vision_integration import process_invoice_complete
        
        result = process_invoice_complete(invoice_file_path, auto_post)
        logger.info(f"End-to-end processing completed successfully")
        return result
    except Exception as error:
        logger.error(f"Error in end-to-end processing: {error}")
        raise Exception(f"Failed to process invoice end-to-end: {str(error)}")

@mcp.resource("quickbooks://about")
def get_about() -> str:
    """Information about the QuickBooks MCP server"""
    return """
QuickBooks MCP Server
--------------------
A complete QuickBooks integration service that enables:
- OAuth authentication with credential persistence
- Full vendor management (CRUD operations)
- Complete bill/invoice management
- Chart of accounts access
- Intelligent vendor matching from invoice data
- Historical coding pattern analysis
- Automated line item coding
- Direct posting to QuickBooks
- End-to-end invoice processing automation

Available tools:
- 'authenticate': Set up QuickBooks OAuth connection
- 'listVendors': Get all vendors with filtering
- 'createVendor': Create new vendor
- 'updateVendor': Update existing vendor
- 'listBills': Get bills with filtering
- 'createBill': Create new bill
- 'updateBill': Update existing bill
- 'getChartOfAccounts': Get all accounts
- 'matchVendorFromInvoice': Match vendor from invoice data
- 'getVendorCodingHistory': Get historical coding patterns
- 'autoCodeInvoice': Automatically code line items
- 'postInvoiceToQuickBooks': Post coded invoice as bill
- 'processInvoiceEnd2End': Complete automation workflow

Integration with Vision MCP:
Seamlessly processes PDFs extracted by Vision MCP server for complete
invoice-to-QuickBooks automation.
"""

if __name__ == "__main__":
    logger.info("Starting QuickBooks MCP server...")
    mcp.run()