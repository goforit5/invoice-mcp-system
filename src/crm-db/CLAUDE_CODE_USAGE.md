# Using CRM MCP Server with Claude Code

This guide explains how to use the CRM Database MCP Server within Claude Code for comprehensive contact management, communication tracking, and financial management.

## Setup for Claude Code

### 1. Installation
```bash
cd /Users/andrew/Projects/claudecode1/src/crm-db
pip install "mcp[cli]" pydantic fastapi python-dateutil
python3 database.py --init --sample-data
```

### 2. MCP Configuration
The CRM server is already configured in the project's `mcp.json` file:
```json
{
  "mcpServers": {
    "crm-db": {
      "command": "python3",
      "args": ["/Users/andrew/Projects/claudecode1/src/crm-db/server.py"],
      "env": {
        "CRM_DB_PATH": "/Users/andrew/Projects/claudecode1/src/crm-db/crm.db"
      }
    }
  }
}
```

### 3. Verification
In Claude Code, you can check if the CRM server is running:
```
/mcp
```
You should see "crm-db" listed as an available MCP server.

## Available Tools

### Contact Management

#### create_contact
Create new contacts with automatic company linking.

**Example**:
```
Create a contact for Sarah Johnson at Acme Corp. Her email is sarah@acme.com, phone is 555-1234, and she's the VP of Marketing. I met her at a conference.
```

**Parameters**:
- `first_name` (required): Contact's first name
- `last_name` (required): Contact's last name  
- `email` (optional): Primary email address
- `phone` (optional): Phone number
- `title` (optional): Job title
- `company_name` (optional): Company name (creates company if doesn't exist)
- `notes` (optional): Additional notes
- `source` (optional): How you met them

#### search_contacts
Find contacts by name, email, or notes.

**Example**:
```
Search for all contacts at Acme Corp
```
```
Find contacts with "developer" in their title or notes
```

**Parameters**:
- `query` (required): Search terms
- `limit` (optional): Max results (default 20)

#### get_contact_timeline
Get complete interaction history for a contact.

**Example**:
```
Show me the complete timeline for contact ID 5, including the last 60 days of activity
```

**Parameters**:
- `contact_id` (required): Contact ID number
- `days_back` (optional): Days of history (default 90)

### Communication Processing

#### create_communication
Record communications from any platform.

**Example**:
```
Log an incoming WhatsApp message from +1-555-0123 saying "Thanks for the meeting today! I'll send the proposal by Friday." The sender is John Smith.
```

**Parameters**:
- `platform` (required): Platform type (email, imessage, whatsapp, instagram_dm, sms, slack, telegram, physical_mail)
- `sender_identifier` (required): Email, phone, username, or address
- `content` (required): Message content
- `subject` (optional): Subject line or topic
- `direction` (optional): 'incoming' or 'outgoing' (default: incoming)
- `sender_name` (optional): Display name
- `timestamp` (optional): ISO timestamp (uses current time if not provided)

#### search_communications
Search all communications by content, sender, or metadata.

**Example**:
```
Find all communications about "project timeline" from the last 2 weeks
```
```
Search for WhatsApp messages from the last 7 days
```

**Parameters**:
- `query` (required): Search terms
- `platform` (optional): Filter by specific platform
- `days_back` (optional): How many days to search (default 30)
- `limit` (optional): Max results (default 20)

### Task Management

#### create_task
Create follow-up tasks and reminders.

**Example**:
```
Create a high priority task to "Follow up on proposal" for contact ID 3, due next Friday with description "Check if they received the proposal and need any clarifications"
```

**Parameters**:
- `title` (required): Task title
- `description` (optional): Detailed description
- `contact_id` (optional): Associated contact
- `company_id` (optional): Associated company
- `due_date` (optional): Due date in YYYY-MM-DD format
- `priority` (optional): low, normal, high, urgent (default: normal)

### Database Operations

#### execute_sql_query
Run read-only SQL queries for custom analysis.

**Example**:
```
Show me all contacts who haven't been contacted in the last 30 days
```
```sql
SELECT c.first_name, c.last_name, c.email, 
       MAX(comm.communication_timestamp) as last_contact
FROM contacts c
LEFT JOIN communications comm ON c.id = comm.sender_contact_id
GROUP BY c.id
HAVING last_contact < date('now', '-30 days') OR last_contact IS NULL
```

**Security**: Only SELECT statements are allowed. INSERT, UPDATE, DELETE are blocked.

## Available Resources

### Schema Information

#### schema://tables
Get complete database schema for understanding the data structure.

**Example**:
```
Show me the database schema so I understand what tables and fields are available
```

### Contact Data

#### contacts://{contact_id}
Get comprehensive contact profile with interaction history.

**Example**:
```
Show me all details for contact ID 2
```

### Dashboard and Reports

#### dashboard://summary
Get CRM overview with key metrics and recent activity.

**Example**:
```
Give me a dashboard summary of my CRM activity
```

#### reports://upcoming_tasks
See tasks due in the next 7 days.

**Example**:
```
What tasks do I have coming up this week?
```

## Practical Usage Examples

### Daily Workflow

**Morning Check-in**:
```
Show me my dashboard summary and upcoming tasks for this week
```

**After Meeting**:
```
Create a communication record for my meeting with John Smith today. We discussed the Q1 budget via phone call. He agreed to send the revised numbers by Thursday.
```

**Follow-up Planning**:
```
Create a task to "Review Q1 budget numbers" due this Thursday with high priority, linked to John Smith's contact
```

### Communication Management

**Log Email Exchange**:
```
Record an incoming email from sarah@techcorp.com with subject "Project Proposal Review" saying "I've reviewed the proposal and have a few questions about the timeline. Can we schedule a call this week?"
```

**Track Text Messages**:
```
Log an incoming SMS from +1-555-0987 saying "Running 10 minutes late for our 2pm meeting" from Mike Davis
```

**Search Communications**:
```
Find all communications about "budget" from the last month
```

### Contact Research

**Find Decision Makers**:
```sql
SELECT c.first_name, c.last_name, c.title, comp.name as company,
       COUNT(comm.id) as interaction_count
FROM contacts c
JOIN companies comp ON c.company_id = comp.id
LEFT JOIN communications comm ON c.id = comm.sender_contact_id
WHERE c.title LIKE '%CEO%' OR c.title LIKE '%VP%' OR c.title LIKE '%Director%'
GROUP BY c.id
ORDER BY interaction_count DESC
```

**Identify Inactive Contacts**:
```
Find contacts I haven't communicated with in the last 60 days
```

### Relationship Management

**Company Analysis**:
```sql
SELECT comp.name, comp.industry,
       COUNT(c.id) as contact_count,
       COUNT(comm.id) as communication_count,
       MAX(comm.communication_timestamp) as last_contact
FROM companies comp
LEFT JOIN contacts c ON comp.id = c.company_id
LEFT JOIN communications comm ON c.id = comm.sender_contact_id
GROUP BY comp.id
ORDER BY communication_count DESC
```

**Contact Engagement Tracking**:
```
Show me the complete timeline for my top 3 most active contacts
```

## Advanced Features

### Cross-Platform Communication Tracking
The system automatically links communications from the same person across different platforms:
- Emails and phone calls from the same contact
- WhatsApp and iMessage from the same phone number
- Instagram DMs and other social platforms

### Smart Contact Matching
When creating communications, the system attempts to automatically match senders to existing contacts:
- Email addresses are matched to contact emails
- Phone numbers are matched across platforms
- Platform usernames are tracked in contact_identities table

### AI-Ready Structure
The database includes fields for AI processing:
- `ai_generated_summary`: LLM summaries of communications
- `ai_extracted_entities`: People, companies, dates, amounts
- `ai_sentiment_score`: Emotional tone analysis

### Financial Integration
Link communications to financial activities:
- Track vendor communications and payments
- Monitor subscription billing contacts
- Analyze business relationship ROI

## Best Practices

### Data Entry
1. **Consistent Contact Creation**: Always include company names when creating contacts
2. **Detailed Communication Logs**: Include context and outcomes in communication records
3. **Task Follow-through**: Create tasks immediately after identifying action items
4. **Regular Reviews**: Use dashboard summary to review activity weekly

### Search Strategy
1. **Use Specific Terms**: Search for specific project names, topics, or keywords
2. **Time-bounded Searches**: Limit searches to relevant time periods
3. **Platform Filtering**: Use platform filters for targeted searches
4. **SQL for Complex Analysis**: Use execute_sql_query for complex reporting needs

### Maintenance
1. **Regular Cleanup**: Periodically review and update contact information
2. **Task Management**: Complete or reschedule overdue tasks
3. **Communication Categorization**: Review and properly categorize important communications
4. **Backup**: Regularly backup your crm.db file

## Troubleshooting

### Common Issues

**"No results found"**: 
- Check spelling in search terms
- Try broader search terms
- Verify data exists in the system

**"Tool not available"**:
- Check that MCP server is running: `/mcp`
- Restart Claude Code if needed
- Verify mcp.json configuration

**"Database error"**:
- Ensure database is initialized: `python3 database.py --init`
- Check file permissions on crm.db
- Verify database isn't corrupted

### Getting Help

If you encounter issues:
1. Check the TESTING.md file for detailed troubleshooting
2. Verify all dependencies are installed
3. Test basic functionality with simple queries
4. Review error messages for specific guidance

The CRM MCP Server provides a powerful foundation for managing all your business and personal relationships through Claude Code!