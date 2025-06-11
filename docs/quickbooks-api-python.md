# QuickBooks API for Vendors and Bills in Python

This document provides a reference for working with QuickBooks API in Python, specifically for handling vendors and bills for accounts payable (AP) transactions.

## Setup and Authentication

```python
from intuitlib.client import AuthClient
from quickbooks import QuickBooks

# Setup authentication client
auth_client = AuthClient(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    environment='sandbox',  # or 'production'
    redirect_uri='YOUR_REDIRECT_URI',
)

# Setup QuickBooks client
client = QuickBooks(
    auth_client=auth_client,
    refresh_token='YOUR_REFRESH_TOKEN',
    company_id='YOUR_COMPANY_ID',
    minorversion=75  # Latest supported version
)
```

## Vendor Management

### Create Vendor
```python
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.base import Address, PhoneNumber, EmailAddress

vendor = Vendor()
vendor.DisplayName = "Acme Supplies"  # Required and must be unique
vendor.CompanyName = "Acme Supplies Inc."
vendor.PrintOnCheckName = "Acme Supplies"
vendor.TaxIdentifier = "99-9999999"  # EIN/SSN 

# Add address
vendor.BillAddr = Address()
vendor.BillAddr.Line1 = "123 Supply St"
vendor.BillAddr.City = "San Francisco"
vendor.BillAddr.CountrySubDivisionCode = "CA"
vendor.BillAddr.PostalCode = "94016"
vendor.BillAddr.Country = "USA"

# Add contact info
vendor.PrimaryPhone = PhoneNumber()
vendor.PrimaryPhone.FreeFormNumber = "555-555-5555"
vendor.PrimaryEmailAddr = EmailAddress()
vendor.PrimaryEmailAddr.Address = "contact@acmesupplies.com"

# Save the vendor
vendor.save(qb=client)
```

### Get Vendor Information
```python
# By ID
vendor = Vendor.get(vendor_id, qb=client)

# Get all vendors
all_vendors = Vendor.all(qb=client)

# Filter vendors
filtered_vendors = Vendor.filter(DisplayName="Acme", qb=client)
active_vendors = Vendor.filter(Active=True, order_by="CompanyName", qb=client)
```

## Bill Management

### Create Bill
```python
from quickbooks.objects.bill import Bill
from quickbooks.objects.detailline import AccountBasedExpenseLine
from quickbooks.objects.account import Account
from quickbooks.helpers import qb_date_format
from datetime import date, timedelta

# Get vendor and account references
vendor = Vendor.get(vendor_id, qb=client)
expense_account = Account.filter(AccountType="Expense", qb=client)[0]

# Create bill
bill = Bill()
bill.VendorRef = vendor.to_ref()
bill.TxnDate = qb_date_format(date.today())
bill.DueDate = qb_date_format(date.today() + timedelta(days=30))

# Create expense line
expense_line = AccountBasedExpenseLine()
expense_line.Amount = 125.50
expense_line.DetailType = "AccountBasedExpenseLineDetail"
expense_line.Description = "Office supplies"

# Set expense account
expense_line.AccountBasedExpenseLineDetail = {}
expense_line.AccountBasedExpenseLineDetail.AccountRef = expense_account.to_ref()

# Add line to bill
bill.Line = [expense_line]

# Save bill
bill.save(qb=client)
```

### Create Bill with Multiple Line Items
```python
bill = Bill()
bill.VendorRef = vendor.to_ref()
bill.TxnDate = qb_date_format(date.today())
bill.DueDate = qb_date_format(date.today() + timedelta(days=30))
bill.Line = []

# Add account-based expense
account_line = AccountBasedExpenseLine()
account_line.Amount = 50.00
account_line.DetailType = "AccountBasedExpenseLineDetail"
account_line.Description = "Office supplies"
account_line.AccountBasedExpenseLineDetail = {}
account_line.AccountBasedExpenseLineDetail.AccountRef = expense_account.to_ref()
bill.Line.append(account_line)

# Add another expense
account_line2 = AccountBasedExpenseLine()
account_line2.Amount = 75.25
account_line2.DetailType = "AccountBasedExpenseLineDetail"
account_line2.Description = "Software subscription"
account_line2.AccountBasedExpenseLineDetail = {}
account_line2.AccountBasedExpenseLineDetail.AccountRef = expense_account.to_ref()
bill.Line.append(account_line2)

# Save bill
bill.save(qb=client)
```

### Query Bills
```python
# Get by ID
bill = Bill.get(bill_id, qb=client)

# Get all bills
all_bills = Bill.all(qb=client)

# Get vendor's bills
vendor_bills = Bill.filter(VendorRef=vendor_id, qb=client)

# Get unpaid bills
unpaid_bills = [bill for bill in Bill.all(qb=client) if bill.Balance > 0]
```

### Pay a Bill
```python
from quickbooks.objects.billpayment import BillPayment, BillPaymentLine, CheckPayment

# Get bill and bank account
bill = Bill.get(bill_id, qb=client)
bank_account = Account.filter(AccountType="Bank", qb=client)[0]

# Create payment
payment = BillPayment()
payment.TotalAmt = bill.Balance
payment.PayType = "Check"  # or "CreditCard"
payment.VendorRef = bill.VendorRef

# Set payment method
payment.CheckPayment = CheckPayment()
payment.CheckPayment.BankAccountRef = bank_account.to_ref()

# Link to bill
payment_line = BillPaymentLine()
payment_line.Amount = bill.Balance
payment_line.LinkedTxn = [{"TxnId": bill.Id, "TxnType": "Bill"}]
payment.Line = [payment_line]

# Save payment
payment.save(qb=client)
```

## Error Handling
```python
from quickbooks.exceptions import QuickbooksException

try:
    vendor.save(qb=client)
except QuickbooksException as e:
    print(f"Error code: {e.error_code}")
    print(f"Message: {e.message}")
    print(f"Detail: {e.detail}")
```

## Installation

The recommended Python library is `python-quickbooks`, which can be installed via pip:
```bash
pip install python-quickbooks intuit-oauth
```

## Resources

For more details, refer to:
- [GitHub repository](https://github.com/ej2/python-quickbooks)
- [PyPI package page](https://pypi.org/project/python-quickbooks/)
- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill)