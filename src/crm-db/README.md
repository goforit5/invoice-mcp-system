# CRM Database MCP Server

A comprehensive Model Context Protocol (MCP) server for managing CRM data, communications, and financial information. Designed specifically for LLM agent interactions with structured data operations.

## Features

### Core CRM
- **Contact Management**: Store and search contacts with company relationships
- **Company Information**: Track business relationships and contact hierarchies
- **Task Management**: Follow-up items with priorities and due dates

### Communication Processing
- **Multi-Platform Support**: Email, iMessage, WhatsApp, Instagram DMs, SMS, Slack, Telegram
- **Universal Inbox**: Unified communication timeline across all platforms
- **Cross-Platform Identity Resolution**: Link same person across different platforms
- **AI Processing**: Sentiment analysis, entity extraction, automated categorization

### Financial Integration
- **Account Management**: Track multiple bank accounts, credit cards
- **Transaction Recording**: Expense and income tracking with categorization
- **Subscription Management**: Recurring service tracking with renewal alerts
- **Budget Monitoring**: Spending analysis and budget vs actual reporting

### LLM-Optimized Design
- **Semantic Field Names**: Clear, descriptive database fields for LLM understanding
- **Structured JSON Responses**: Consistent data formats for AI processing
- **Rich Context**: Comprehensive metadata for informed decision-making
- **Search Capabilities**: Full-text search across communications and contacts

## Installation

1. **Install Dependencies**:
   ```bash
   cd src/crm-db
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python database.py --init --sample-data
   ```

3. **Test Server**:
   ```bash
   python server.py
   ```

## MCP Configuration

Add to your MCP configuration (`.mcp.json` or Claude Desktop settings):

```json
{
  "mcpServers": {
    "crm-db": {
      "command": "python",
      "args": ["/Users/andrew/Projects/claudecode1/src/crm-db/server.py"],
      "env": {
        "CRM_DB_PATH": "/Users/andrew/Projects/claudecode1/src/crm-db/crm.db"
      }
    }
  }
}
```

## MCP Tools

### Contact Management
- `create_contact(first_name, last_name, email, phone, title, company_name, notes, source)` - Create new contact
- `search_contacts(query, limit)` - Search contacts by name, email, or notes
- `get_contact_timeline(contact_id, days_back)` - Get complete contact history

### Communication Processing
- `create_communication(platform, sender_identifier, content, subject, direction, sender_name, timestamp)` - Record communication
- `search_communications(query, platform, days_back, limit)` - Search message content

### Task Management
- `create_task(title, description, contact_id, company_id, due_date, priority)` - Create follow-up task

### Database Operations
- `execute_sql_query(sql)` - Execute read-only SQL queries (SELECT only)

## MCP Resources

### Schema Information
- `schema://tables` - Complete database schema for LLM understanding

### Contact Data
- `contacts://{contact_id}` - Comprehensive contact profile with history

### Dashboard Views
- `dashboard://summary` - CRM metrics and recent activity overview
- `reports://upcoming_tasks` - Tasks due in next 7 days

## Database Schema

The database includes 13 tables optimized for LLM processing:

### Core Tables
- `contacts` - Contact information and relationships
- `companies` - Business organization data
- `interactions` - Manual interaction logging
- `tasks` - Follow-up items and action tracking
- `tags` & `contact_tags` - Flexible categorization

### Financial Tables
- `accounts` - Bank accounts and financial institutions
- `transactions` - Income and expense records
- `subscriptions` - Recurring service billing
- `budgets` - Spending limits and categories

### Communication Tables
- `communications` - Universal communication records
- `communication_attachments` - Media and file storage
- `contact_identities` - Cross-platform identity mapping
- `communication_processing_log` - AI processing audit trail

## Usage Examples

### Create a Contact
```python
# Through MCP tool
result = create_contact(
    first_name="John",
    last_name="Smith", 
    email="john@acme.com",
    company_name="Acme Corp",
    title="CEO"
)
```

### Record Communication
```python
# Log an incoming WhatsApp message
result = create_communication(
    platform="whatsapp",
    sender_identifier="+1234567890",
    content="Hey, can we reschedule our meeting to Thursday?",
    direction="incoming",
    sender_name="John Smith"
)
```

### Search Communications
```python
# Find all messages about meetings
results = search_communications(
    query="meeting schedule",
    days_back=14
)
```

### Get Contact Timeline
```python
# Complete interaction history
timeline = get_contact_timeline(
    contact_id=123,
    days_back=90
)
```

## Advanced Features

### Cross-Platform Identity Resolution
The system automatically links communications from the same person across different platforms:
- Email: john@acme.com
- WhatsApp: +1234567890  
- iMessage: +1234567890
- Instagram: @johnsmith

### AI Processing Integration
Built-in fields for AI enhancement:
- `ai_generated_summary` - LLM summaries of communications
- `ai_extracted_entities` - People, companies, dates, amounts
- `ai_sentiment_score` - Emotional tone analysis
- Processing cost tracking for LLM operations

### Communication Categories
Automatic categorization:
- `business` - Work-related communications
- `personal` - Personal messages
- `financial` - Bills, invoices, payments
- `legal` - Contracts, legal documents
- `marketing` - Promotional content

### Task Automation
Tasks are automatically created from:
- Bills requiring payment (from scanned mail)
- Follow-up requests in communications
- Meeting scheduling needs
- Document review requirements

## Security Features

- **SQL Injection Protection**: Parameterized queries throughout
- **Read-Only Query Tool**: `execute_sql_query` only allows SELECT statements
- **Input Validation**: Pydantic models for all data operations
- **Error Handling**: Comprehensive error logging and user feedback

## Development

### Running Tests
```bash
# Initialize test database
python database.py --init --sample-data --db-path test_crm.db

# Run server in development mode
python server.py
```

### Adding New Communication Platforms
1. Add platform to `Platform` enum in `models.py`
2. Create processor in `processors/` directory
3. Update communication creation logic in `server.py`

### Database Migrations
The database automatically initializes with the latest schema. For production use, implement proper migration scripts for schema updates.

## Integration Points

### With Existing MCP Servers
- **Vision MCP**: OCR scanned documents → create communications
- **QuickBooks MCP**: Link financial transactions to CRM contacts
- **Email Providers**: Import email communications automatically

### With External Systems
- **Calendar Integration**: Sync meeting tasks with calendar apps
- **Email Platforms**: Gmail, Outlook integration for communication import
- **Financial Apps**: Bank transaction import and categorization

## Troubleshooting

### Common Issues

1. **Database Lock Errors**: Ensure only one connection modifies data at a time
2. **FTS Search Failing**: Falls back to LIKE search automatically
3. **Large Attachments**: Configure file storage paths appropriately

### Logging
Server logs include:
- Database operations
- MCP tool invocations  
- Error conditions with stack traces
- Performance metrics

### Performance Optimization
- Database indexes on frequently queried fields
- FTS5 tables for fast text search
- Connection pooling for high-volume operations
- Lazy loading of attachment content

## License

This MCP server is part of the Claude MCP Servers project.