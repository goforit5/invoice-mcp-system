# CRM MCP Server Testing Guide

Complete testing instructions for the CRM Database MCP Server designed for Claude Code.

## Quick Start Testing

### 1. Install Dependencies
```bash
cd /Users/andrew/Projects/claudecode1/src/crm-db
pip install "mcp[cli]" pydantic fastapi python-dateutil fuzzywuzzy python-Levenshtein
```

### 2. Initialize Database
```bash
# Create database with schema and sample data
python3 database.py --init --sample-data

# Or create empty database
python3 database.py --init
```

### 3. Run Basic Tests
```bash
# Test all components
python3 run_tests.py

# Simple validation test
python3 simple_test.py

# Initialize and verify database
python3 init_and_test.py

# Basic validation only
python3 validate.py
```

### 4. Test MCP Server
```bash
# Start the MCP server (should not exit if working)
python3 server.py

# Test with MCP dev tools (if installed)
mcp dev server.py
```

## Detailed Testing Procedures

### Database Testing

#### Test 1: Schema Creation
```bash
python3 -c "
from database import CRMDatabase
db = CRMDatabase('test.db')
with db:
    db.init_database()
    cursor = db.conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = [row[0] for row in cursor.fetchall()]
    print(f'Created {len(tables)} tables: {tables}')
import os; os.unlink('test.db')
"
```

Expected output: Should list 13+ tables including contacts, companies, communications, etc.

#### Test 2: Sample Data
```bash
python3 -c "
from database import CRMDatabase
db = CRMDatabase('test.db')
with db:
    db.init_database()
    db.create_sample_data()
    cursor = db.conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM contacts')
    contacts = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM companies')
    companies = cursor.fetchone()[0]
    print(f'Sample data: {contacts} contacts, {companies} companies')
import os; os.unlink('test.db')
"
```

Expected output: Should show contact and company counts (3 contacts, 3 companies typically).

### Model Testing

#### Test 3: Pydantic Models
```bash
python3 -c "
from models import Contact, Communication, Platform, Direction
from datetime import datetime

# Test Contact
contact = Contact(first_name='John', last_name='Doe', email='john@test.com')
print(f'Contact: {contact.full_name}')

# Test Communication  
comm = Communication(
    platform=Platform.email,
    sender_identifier='john@test.com',
    message_content_text='Hello',
    direction=Direction.incoming,
    communication_timestamp=datetime.now()
)
print(f'Communication: {comm.platform} from {comm.sender_identifier}')
print('✅ Models working correctly')
"
```

Expected output: Should create and display contact and communication objects.

### Server Testing

#### Test 4: Server Import
```bash
python3 -c "
try:
    import server
    print('✅ Server imports successfully')
    if hasattr(server, 'mcp'):
        print(f'FastMCP server: {server.mcp.name}')
    else:
        print('⚠️ FastMCP not available (MCP package may not be installed)')
except Exception as e:
    print(f'❌ Server import failed: {e}')
"
```

Expected output: Should import successfully. May warn about MCP if not installed.

#### Test 5: Database Operations via Server Functions
```bash
python3 -c "
import sys, os
sys.path.append('.')
from database import CRMDatabase

# Initialize test database
db = CRMDatabase('test_server.db')
with db:
    db.init_database()
    db.create_sample_data()

# Test server helper functions
from server import get_db_connection, format_results_for_llm, safe_execute

# Override DB_PATH for testing
import server
server.DB_PATH = 'test_server.db'

conn = get_db_connection()
results = safe_execute(conn, 'SELECT * FROM contacts LIMIT 2')
formatted = format_results_for_llm(results, 'Test query')
print('✅ Server functions working')
print(f'Found {len(results)} results')
conn.close()

os.unlink('test_server.db')
"
```

## Integration Testing

### Test with Claude Code

1. **Setup MCP Server**:
   ```bash
   # Ensure database exists
   python3 database.py --init --sample-data
   
   # The mcp.json is already configured for Claude Code
   ```

2. **Test MCP Tools** (in Claude Code):
   ```
   Use the create_contact tool to create a new contact
   Use the search_contacts tool to find contacts
   Use the create_communication tool to log a message
   Use the get_contact_timeline tool to see contact history
   ```

3. **Test MCP Resources** (in Claude Code):
   ```
   Access schema://tables to see database schema
   Access dashboard://summary for CRM overview
   Access contacts://1 to see contact details
   ```

### Expected MCP Tools Available

When working correctly, Claude Code should have access to these tools:

- **create_contact**: Create new contacts with optional company
- **search_contacts**: Search contacts by name, email, notes
- **create_communication**: Record communications from any platform
- **search_communications**: Search message content and metadata
- **get_contact_timeline**: Complete interaction history for a contact
- **create_task**: Create follow-up tasks and reminders
- **execute_sql_query**: Run read-only SQL queries safely

### Expected MCP Resources Available

- **schema://tables**: Complete database schema for LLM understanding
- **contacts://{id}**: Detailed contact profiles with history
- **dashboard://summary**: CRM metrics and recent activity
- **reports://upcoming_tasks**: Tasks due in next 7 days

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'mcp'"
**Solution**: Install MCP package
```bash
pip install "mcp[cli]"
```

#### "ModuleNotFoundError: No module named 'pydantic'"
**Solution**: Install missing dependencies
```bash
pip install pydantic fastapi python-dateutil
```

#### "OperationalError: no such table: contacts"
**Solution**: Initialize database
```bash
python3 database.py --init --sample-data
```

#### "Database is locked"
**Solution**: Close any open connections
```bash
# Remove any existing database and recreate
rm crm.db
python3 database.py --init --sample-data
```

#### Server starts but tools not available in Claude Code
**Solution**: Check MCP configuration
1. Verify `mcp.json` has correct paths
2. Restart Claude Code application
3. Check Claude Code MCP status

### Performance Testing

#### Large Dataset Test
```bash
python3 -c "
from database import CRMDatabase
import random
from datetime import datetime, timedelta

db = CRMDatabase('large_test.db')
with db:
    db.init_database()
    
    # Create many contacts
    for i in range(1000):
        db.conn.execute('''
            INSERT INTO contacts (first_name, last_name, email)
            VALUES (?, ?, ?)
        ''', (f'User{i}', f'Test{i}', f'user{i}@test.com'))
    
    # Create many communications
    for i in range(5000):
        db.conn.execute('''
            INSERT INTO communications (
                platform, sender_identifier, message_content_text,
                direction, communication_timestamp
            ) VALUES (?, ?, ?, ?, ?)
        ''', ('email', f'user{i%1000}@test.com', f'Message {i}',
              'incoming', datetime.now() - timedelta(days=random.randint(0, 365))))
    
    db.conn.commit()
    
    # Test query performance
    import time
    start = time.time()
    result = db.conn.execute('SELECT COUNT(*) FROM communications').fetchone()
    end = time.time()
    
    print(f'Query performance: {end-start:.3f}s for {result[0]} records')

import os; os.unlink('large_test.db')
"
```

## Success Criteria

The CRM MCP Server is working correctly when:

✅ **Database Tests Pass**:
- Schema creates all 13+ tables
- Sample data inserts successfully
- Queries return expected results
- Foreign key relationships work

✅ **Model Tests Pass**:
- Pydantic models validate correctly
- Enums work with proper values
- Model relationships function

✅ **Server Tests Pass**:
- Server module imports without errors
- FastMCP server initializes (if MCP installed)
- Helper functions work correctly

✅ **MCP Integration Works**:
- Tools are available in Claude Code
- Resources are accessible
- Database operations succeed through MCP
- Error handling works properly

✅ **Performance Acceptable**:
- Database queries complete in <1 second
- Large datasets (1000+ records) perform well
- Memory usage remains reasonable

## Next Steps

Once all tests pass:

1. **Use with Claude Code**: The server is ready for production use
2. **Add Custom Data**: Use MCP tools to add your real contacts and communications
3. **Extend Functionality**: Add custom tools for specific workflows
4. **Monitor Performance**: Watch for any performance issues with large datasets
5. **Backup Data**: Regularly backup your `crm.db` file

## Support

If tests fail or you encounter issues:

1. Check the error messages carefully
2. Verify all dependencies are installed
3. Ensure file permissions are correct
4. Review the troubleshooting section above
5. Check the main README.md for additional setup information