"""
QuickBooks API integration for automated invoice processing
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.bill import Bill
from quickbooks.objects.account import Account
from quickbooks.objects.detailline import AccountBasedExpenseLine
from quickbooks.helpers import qb_date_format
from quickbooks.exceptions import QuickbooksException

# Configure logging
logger = logging.getLogger(__name__)

# Global QuickBooks client
qb_client = None
auth_data = {}

def load_auth_data():
    """Load saved authentication data"""
    global auth_data
    auth_file = Path(__file__).parent / "qb_auth.json"
    
    if auth_file.exists():
        with open(auth_file, 'r') as f:
            auth_data = json.load(f)
    return auth_data

def save_auth_data(data):
    """Save authentication data securely"""
    global auth_data
    auth_data = data
    auth_file = Path(__file__).parent / "qb_auth.json"
    
    with open(auth_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Set secure permissions
    os.chmod(auth_file, 0o600)

def get_qb_client():
    """Get authenticated QuickBooks client"""
    global qb_client
    
    if qb_client is None:
        auth_data = load_auth_data()
        if not auth_data:
            raise Exception("No authentication data found. Please authenticate first.")
        
        auth_client = AuthClient(
            client_id=auth_data['client_id'],
            client_secret=auth_data['client_secret'],
            environment=auth_data['environment'],
            redirect_uri=auth_data['redirect_uri']
        )
        
        qb_client = QuickBooks(
            auth_client=auth_client,
            refresh_token=auth_data['refresh_token'],
            company_id=auth_data['company_id'],
            minorversion=75
        )
    
    return qb_client

def authenticate_quickbooks(client_id: str, client_secret: str, redirect_uri: str, environment: str = "sandbox") -> Dict:
    """
    Authenticate with QuickBooks and save credentials
    """
    try:
        # Save initial auth data
        initial_auth_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'environment': environment,
            'redirect_uri': redirect_uri
        }
        save_auth_data(initial_auth_data)
        
        # Create auth client
        auth_client = AuthClient(
            client_id=client_id,
            client_secret=client_secret,
            environment=environment,
            redirect_uri=redirect_uri
        )
        
        # Generate authorization URL
        auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        
        return {
            "status": "authorization_required",
            "auth_url": auth_url,
            "message": "Please visit the authorization URL and complete OAuth flow",
            "next_step": "After authorization, call complete_authentication with the authorization code"
        }
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise Exception(f"Failed to start authentication: {str(e)}")

def complete_authentication(auth_code: str, realm_id: str) -> Dict:
    """
    Complete OAuth flow and save tokens
    """
    try:
        auth_data = load_auth_data()
        if not auth_data:
            raise Exception("No pending authentication found")
        
        auth_client = AuthClient(
            client_id=auth_data['client_id'],
            client_secret=auth_data['client_secret'],
            environment=auth_data['environment'],
            redirect_uri=auth_data['redirect_uri']
        )
        
        # Exchange code for tokens
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        
        # Save complete auth data
        complete_auth_data = {
            **auth_data,
            'access_token': auth_client.access_token,
            'refresh_token': auth_client.refresh_token,
            'company_id': realm_id,
            'authenticated_at': datetime.now().isoformat()
        }
        
        save_auth_data(complete_auth_data)
        
        return {
            "status": "authenticated",
            "company_id": realm_id,
            "message": "Successfully authenticated with QuickBooks"
        }
        
    except Exception as e:
        logger.error(f"Authentication completion error: {e}")
        raise Exception(f"Failed to complete authentication: {str(e)}")

def get_vendors(active_only: bool = True) -> List[Dict]:
    """Get all vendors from QuickBooks"""
    try:
        client = get_qb_client()
        
        if active_only:
            vendors = Vendor.filter(Active=True, qb=client)
        else:
            vendors = Vendor.all(qb=client)
        
        return [vendor_to_dict(vendor) for vendor in vendors]
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error getting vendors: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error getting vendors: {e}")
        raise Exception(f"Failed to get vendors: {str(e)}")

def create_vendor(vendor_data: Dict) -> Dict:
    """Create a new vendor in QuickBooks"""
    try:
        client = get_qb_client()
        
        vendor = Vendor()
        vendor.DisplayName = vendor_data['DisplayName']
        
        # Optional fields
        if 'CompanyName' in vendor_data:
            vendor.CompanyName = vendor_data['CompanyName']
        if 'PrintOnCheckName' in vendor_data:
            vendor.PrintOnCheckName = vendor_data['PrintOnCheckName']
        if 'TaxIdentifier' in vendor_data:
            vendor.TaxIdentifier = vendor_data['TaxIdentifier']
            
        # Address handling
        if 'Address' in vendor_data:
            from quickbooks.objects.base import Address
            vendor.BillAddr = Address()
            addr_data = vendor_data['Address']
            for field in ['Line1', 'Line2', 'City', 'CountrySubDivisionCode', 'PostalCode', 'Country']:
                if field in addr_data:
                    setattr(vendor.BillAddr, field, addr_data[field])
        
        # Contact info
        if 'Phone' in vendor_data:
            from quickbooks.objects.base import PhoneNumber
            vendor.PrimaryPhone = PhoneNumber()
            vendor.PrimaryPhone.FreeFormNumber = vendor_data['Phone']
            
        if 'Email' in vendor_data:
            from quickbooks.objects.base import EmailAddress
            vendor.PrimaryEmailAddr = EmailAddress()
            vendor.PrimaryEmailAddr.Address = vendor_data['Email']
        
        vendor.save(qb=client)
        return vendor_to_dict(vendor)
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error creating vendor: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error creating vendor: {e}")
        raise Exception(f"Failed to create vendor: {str(e)}")

def update_vendor(vendor_id: str, vendor_data: Dict) -> Dict:
    """Update an existing vendor in QuickBooks"""
    try:
        client = get_qb_client()
        
        vendor = Vendor.get(vendor_id, qb=client)
        
        # Update fields
        for field in ['DisplayName', 'CompanyName', 'PrintOnCheckName', 'TaxIdentifier']:
            if field in vendor_data:
                setattr(vendor, field, vendor_data[field])
        
        vendor.save(qb=client)
        return vendor_to_dict(vendor)
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error updating vendor: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error updating vendor: {e}")
        raise Exception(f"Failed to update vendor: {str(e)}")

def get_bills(vendor_id: str = None, unpaid_only: bool = False) -> List[Dict]:
    """Get bills from QuickBooks"""
    try:
        client = get_qb_client()
        
        if vendor_id:
            bills = Bill.filter(VendorRef=vendor_id, qb=client)
        else:
            bills = Bill.all(qb=client)
        
        if unpaid_only:
            bills = [bill for bill in bills if bill.Balance > 0]
        
        return [bill_to_dict(bill) for bill in bills]
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error getting bills: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error getting bills: {e}")
        raise Exception(f"Failed to get bills: {str(e)}")

def create_bill(bill_data: Dict) -> Dict:
    """Create a new bill in QuickBooks"""
    try:
        client = get_qb_client()
        
        bill = Bill()
        
        # Set vendor reference
        if 'VendorRef' in bill_data:
            bill.VendorRef = bill_data['VendorRef']
        else:
            raise ValueError("VendorRef is required for bill creation")
        
        # Set dates
        bill.TxnDate = bill_data.get('TxnDate', qb_date_format(datetime.now().date()))
        if 'DueDate' in bill_data:
            bill.DueDate = bill_data['DueDate']
        else:
            # Default to 30 days from transaction date
            due_date = datetime.now().date() + timedelta(days=30)
            bill.DueDate = qb_date_format(due_date)
        
        # Add line items
        if 'LineItems' in bill_data:
            bill.Line = []
            for line_item in bill_data['LineItems']:
                line = AccountBasedExpenseLine()
                line.Amount = line_item['Amount']
                line.DetailType = "AccountBasedExpenseLineDetail"
                line.Description = line_item.get('Description', '')
                
                line.AccountBasedExpenseLineDetail = {}
                line.AccountBasedExpenseLineDetail.AccountRef = line_item['AccountRef']
                
                bill.Line.append(line)
        
        bill.save(qb=client)
        return bill_to_dict(bill)
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error creating bill: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error creating bill: {e}")
        raise Exception(f"Failed to create bill: {str(e)}")

def update_bill(bill_id: str, bill_data: Dict) -> Dict:
    """Update an existing bill in QuickBooks"""
    try:
        client = get_qb_client()
        
        bill = Bill.get(bill_id, qb=client)
        
        # Update fields as needed
        # Implementation depends on specific update requirements
        
        bill.save(qb=client)
        return bill_to_dict(bill)
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error updating bill: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error updating bill: {e}")
        raise Exception(f"Failed to update bill: {str(e)}")

def get_chart_of_accounts(active_only: bool = True) -> List[Dict]:
    """Get chart of accounts from QuickBooks"""
    try:
        client = get_qb_client()
        
        if active_only:
            accounts = Account.filter(Active=True, qb=client)
        else:
            accounts = Account.all(qb=client)
        
        return [account_to_dict(account) for account in accounts]
        
    except QuickbooksException as e:
        logger.error(f"QuickBooks API error getting accounts: {e}")
        raise Exception(f"QuickBooks error: {e.message}")
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise Exception(f"Failed to get accounts: {str(e)}")

def match_vendor(invoice_data: Dict) -> Dict:
    """Match vendor from invoice data"""
    try:
        vendor_name = invoice_data.get('vendor_name', '').strip()
        if not vendor_name:
            return {"status": "no_vendor_name", "message": "No vendor name found in invoice"}
        
        # Get all vendors and try to match
        vendors = get_vendors(active_only=True)
        
        # Exact match first
        for vendor in vendors:
            if vendor['DisplayName'].lower() == vendor_name.lower():
                return {
                    "status": "exact_match",
                    "vendor": vendor,
                    "confidence": 1.0
                }
        
        # Partial match
        matches = []
        for vendor in vendors:
            if vendor_name.lower() in vendor['DisplayName'].lower() or vendor['DisplayName'].lower() in vendor_name.lower():
                matches.append(vendor)
        
        if matches:
            return {
                "status": "partial_matches", 
                "matches": matches,
                "confidence": 0.7
            }
        
        # No match - suggest creating new vendor
        return {
            "status": "no_match",
            "suggestion": {
                "DisplayName": vendor_name,
                "CompanyName": vendor_name
            },
            "message": "No matching vendor found. Consider creating new vendor."
        }
        
    except Exception as e:
        logger.error(f"Error matching vendor: {e}")
        raise Exception(f"Failed to match vendor: {str(e)}")

def get_vendor_history(vendor_id: str, limit: int = 10) -> Dict:
    """Get vendor's historical coding patterns"""
    try:
        bills = get_bills(vendor_id=vendor_id)
        
        # Analyze recent bills for coding patterns
        account_usage = {}
        recent_bills = sorted(bills, key=lambda x: x.get('TxnDate', ''), reverse=True)[:limit]
        
        for bill in recent_bills:
            for line in bill.get('LineItems', []):
                account_ref = line.get('AccountRef', {})
                account_name = account_ref.get('name', 'Unknown')
                
                if account_name not in account_usage:
                    account_usage[account_name] = {
                        "count": 0,
                        "total_amount": 0,
                        "account_ref": account_ref
                    }
                
                account_usage[account_name]["count"] += 1
                account_usage[account_name]["total_amount"] += float(line.get('Amount', 0))
        
        # Sort by usage frequency
        sorted_accounts = sorted(account_usage.items(), key=lambda x: x[1]['count'], reverse=True)
        
        return {
            "vendor_id": vendor_id,
            "bills_analyzed": len(recent_bills),
            "account_patterns": dict(sorted_accounts),
            "most_used_account": sorted_accounts[0] if sorted_accounts else None
        }
        
    except Exception as e:
        logger.error(f"Error getting vendor history: {e}")
        raise Exception(f"Failed to get vendor history: {str(e)}")

def auto_code_invoice(invoice_data: Dict, vendor_id: str = None) -> Dict:
    """Automatically code invoice line items"""
    try:
        # Get chart of accounts
        accounts = get_chart_of_accounts(active_only=True)
        
        # Get vendor history if available
        vendor_patterns = {}
        if vendor_id:
            history = get_vendor_history(vendor_id)
            vendor_patterns = history.get('account_patterns', {})
        
        coded_items = []
        
        for item in invoice_data.get('line_items', []):
            description = item.get('description', '').lower()
            amount = item.get('amount', 0)
            
            # Try to match based on description keywords
            suggested_account = None
            confidence = 0
            
            # Check vendor patterns first
            if vendor_patterns:
                most_used = max(vendor_patterns.items(), key=lambda x: x[1]['count'])
                suggested_account = most_used[1]['account_ref']
                confidence = 0.8
            
            # Try keyword matching
            expense_keywords = {
                'office supplies': ['office', 'supplies', 'paper', 'pen'],
                'utilities': ['electric', 'gas', 'water', 'utility'],
                'travel': ['travel', 'hotel', 'flight', 'mileage'],
                'meals': ['meal', 'restaurant', 'food', 'dining'],
                'software': ['software', 'subscription', 'saas', 'license']
            }
            
            for account_type, keywords in expense_keywords.items():
                if any(keyword in description for keyword in keywords):
                    # Find matching account
                    for account in accounts:
                        if account_type.replace(' ', '').lower() in account['Name'].lower().replace(' ', ''):
                            suggested_account = {
                                "value": account['Id'],
                                "name": account['Name']
                            }
                            confidence = 0.6
                            break
                    break
            
            # Default to general expense if no match
            if not suggested_account:
                expense_accounts = [acc for acc in accounts if 'expense' in acc['Name'].lower()]
                if expense_accounts:
                    suggested_account = {
                        "value": expense_accounts[0]['Id'],
                        "name": expense_accounts[0]['Name']
                    }
                    confidence = 0.3
            
            coded_items.append({
                **item,
                "suggested_account": suggested_account,
                "confidence": confidence,
                "requires_review": confidence < 0.7
            })
        
        return {
            "original_invoice": invoice_data,
            "coded_line_items": coded_items,
            "vendor_id": vendor_id,
            "coding_confidence": sum(item['confidence'] for item in coded_items) / len(coded_items) if coded_items else 0
        }
        
    except Exception as e:
        logger.error(f"Error auto-coding invoice: {e}")
        raise Exception(f"Failed to auto-code invoice: {str(e)}")

def post_to_quickbooks(coded_invoice_data: Dict, auto_post: bool = False) -> Dict:
    """Post coded invoice to QuickBooks as a bill"""
    try:
        invoice = coded_invoice_data['original_invoice']
        line_items = coded_invoice_data['coded_line_items']
        
        # Check if all line items have confident coding
        requires_review = any(item.get('requires_review', False) for item in line_items)
        
        if requires_review and not auto_post:
            return {
                "status": "review_required",
                "message": "Some line items have low confidence coding and require review",
                "line_items_for_review": [item for item in line_items if item.get('requires_review', False)]
            }
        
        # Create bill data
        bill_data = {
            "VendorRef": {
                "value": coded_invoice_data.get('vendor_id'),
                "name": invoice.get('vendor_name')
            },
            "TxnDate": qb_date_format(datetime.now().date()),
            "LineItems": []
        }
        
        # Add due date if available
        if 'due_date' in invoice:
            bill_data['DueDate'] = invoice['due_date']
        
        # Convert line items
        for item in line_items:
            if item.get('suggested_account'):
                bill_data["LineItems"].append({
                    "Amount": item['amount'],
                    "Description": item.get('description', ''),
                    "AccountRef": item['suggested_account']
                })
        
        # Create the bill
        bill = create_bill(bill_data)
        
        return {
            "status": "posted",
            "bill_id": bill['Id'],
            "bill_data": bill,
            "message": f"Successfully posted bill to QuickBooks with ID: {bill['Id']}"
        }
        
    except Exception as e:
        logger.error(f"Error posting to QuickBooks: {e}")
        raise Exception(f"Failed to post to QuickBooks: {str(e)}")

# Helper functions to convert QB objects to dictionaries
def vendor_to_dict(vendor) -> Dict:
    """Convert QB Vendor object to dictionary"""
    return {
        "Id": getattr(vendor, 'Id', None),
        "DisplayName": getattr(vendor, 'DisplayName', ''),
        "CompanyName": getattr(vendor, 'CompanyName', ''),
        "Active": getattr(vendor, 'Active', True),
        "TaxIdentifier": getattr(vendor, 'TaxIdentifier', ''),
        "PrintOnCheckName": getattr(vendor, 'PrintOnCheckName', ''),
        "Balance": getattr(vendor, 'Balance', 0)
    }

def bill_to_dict(bill) -> Dict:
    """Convert QB Bill object to dictionary"""
    return {
        "Id": getattr(bill, 'Id', None),
        "VendorRef": getattr(bill, 'VendorRef', {}),
        "TxnDate": getattr(bill, 'TxnDate', ''),
        "DueDate": getattr(bill, 'DueDate', ''),
        "TotalAmt": getattr(bill, 'TotalAmt', 0),
        "Balance": getattr(bill, 'Balance', 0),
        "LineItems": [line_to_dict(line) for line in getattr(bill, 'Line', [])]
    }

def line_to_dict(line) -> Dict:
    """Convert QB Line object to dictionary"""
    return {
        "Amount": getattr(line, 'Amount', 0),
        "Description": getattr(line, 'Description', ''),
        "AccountRef": getattr(line, 'AccountBasedExpenseLineDetail', {}).get('AccountRef', {})
    }

def account_to_dict(account) -> Dict:
    """Convert QB Account object to dictionary"""
    return {
        "Id": getattr(account, 'Id', None),
        "Name": getattr(account, 'Name', ''),
        "AccountType": getattr(account, 'AccountType', ''),
        "AccountSubType": getattr(account, 'AccountSubType', ''),
        "Active": getattr(account, 'Active', True),
        "CurrentBalance": getattr(account, 'CurrentBalance', 0)
    }