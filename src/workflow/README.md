# Workflow Orchestration MCP Server

## Overview

The Workflow Orchestration MCP Server provides automated workflow management across multiple MCP servers. It enables you to create declarative workflows that chain operations across CRM, Vision, QuickBooks, and other MCP services with AI-powered processing.

## Key Features

- **Cross-MCP Orchestration**: Chain operations across multiple MCP servers
- **Event-Driven Architecture**: Trigger workflows based on events (document processed, communication created, etc.)
- **AI-Powered Processing**: Built-in AI tools for summarization, entity extraction, and classification
- **Declarative Workflows**: Define workflows in YAML with conditional logic
- **Full Audit Trail**: Complete execution history with step-by-step results
- **Parameter Resolution**: Dynamic parameter resolution from context and previous steps

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vision MCP    │    │   CRM-DB MCP    │    │ QuickBooks MCP  │
│                 │    │                 │    │                 │
│ • Extract Data  │    │ • Store Records │    │ • Match Vendors │
│ • OCR Text      │    │ • Track Tasks   │    │ • Create Bills  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Workflow Engine │
                    │                 │
                    │ • Orchestrate   │
                    │ • AI Process    │
                    │ • Execute Steps │
                    │ • Audit Trail   │
                    └─────────────────┘
```

## Workflow Definition Format

Workflows are defined in YAML files in the `workflows/` directory:

```yaml
name: "DMV Document Processing"
description: "Automated processing of DMV notices"

triggers:
  - event: "communication.created"
    conditions:
      - "sender_identifier LIKE '%dmv%'"
      - "content LIKE '%suspend%'"

steps:
  - name: "ai_summary"
    tool: "ai_summarize"
    params:
      content: "${trigger_data.message_content_text}"
      max_length: 200
    
  - name: "extract_entities"
    tool: "ai_extract_entities"
    params:
      content: "${trigger_data.message_content_text}"
      types: ["dates", "amounts", "vehicles"]
    
  - name: "create_task"
    tool: "crm_create_task"
    conditions:
      - "urgency_level IN ('high', 'urgent')"
    params:
      title: "DMV Action Required"
      due_date: "${execution_results.extract_entities.entities.deadlines[0]}"
```

## Available Tools

### AI Processing Tools
- `ai_summarize`: Generate concise summaries of content
- `ai_extract_entities`: Extract structured entities (dates, amounts, etc.)
- `ai_classify_urgency`: Determine urgency level based on keywords

### CRM Tools
- `crm_create_contact`: Create new contact records
- `crm_create_company`: Create new company records
- `crm_create_task`: Create follow-up tasks
- `crm_update_communication`: Update communication fields
- `crm_create_communication`: Log new communications

### Vision Tools
- `vision_extract_invoice`: Extract structured data from invoices
- `vision_extract_document`: General document text extraction

### QuickBooks Tools
- `quickbooks_match_vendor`: Match vendors from invoice data
- `quickbooks_create_bill`: Create bills in QuickBooks
- `quickbooks_auto_code`: Automatically code invoice line items

## MCP Tools

### `trigger_workflow`
Manually trigger a workflow execution.

```python
trigger_workflow(
    workflow_name="DMV Document Processing",
    trigger_event="communication.created",
    trigger_data={
        "id": 4,
        "sender_identifier": "dmv.ca.gov",
        "content": "Notice of suspension..."
    }
)
```

### `list_workflows`
List all available workflow definitions.

### `get_workflow_execution`
Get detailed execution results for a specific workflow run.

### `create_workflow_definition`
Create a new workflow definition programmatically.

## Usage Examples

### 1. DMV Document Processing

When a DMV communication is created, automatically:
1. Generate AI summary
2. Extract key entities (dates, vehicle info, amounts)
3. Classify urgency level
4. Create follow-up task if urgent
5. Update communication with AI insights

### 2. Invoice Processing

When an invoice is uploaded:
1. Extract data using Vision MCP
2. Match vendor in QuickBooks
3. Auto-code line items
4. Create CRM task for approval
5. Log communication history

### 3. Legal Notice Processing

When legal documents are received:
1. Extract key dates and requirements
2. Create high-priority tasks
3. Set calendar reminders
4. Update contact records
5. Generate summary reports

## Parameter Resolution

Workflows support dynamic parameter resolution:

- `${trigger_data.field}`: Access trigger event data
- `${execution_results.step_name.result}`: Use results from previous steps
- `${execution_id}`: Current execution ID
- Static values: Direct value assignment

## Conditional Execution

Steps can include conditions for smart execution:

```yaml
- name: "urgent_notification"
  tool: "send_notification"
  conditions:
    - "urgency_level IN ('high', 'urgent')"
    - "amount > 1000"
  params:
    message: "Urgent: ${trigger_data.subject}"
```

## Execution Flow

1. **Trigger**: Event occurs (document processed, communication created)
2. **Match**: Check workflow triggers and conditions
3. **Execute**: Run workflow steps sequentially
4. **Resolve**: Dynamic parameter resolution from context
5. **Route**: Call appropriate MCP server tools
6. **Audit**: Log all results and errors
7. **Complete**: Mark execution as completed/failed

## Database Schema

Workflow executions are stored with full audit trails:

```sql
CREATE TABLE workflow_executions (
    execution_id TEXT PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    trigger_event TEXT NOT NULL,
    trigger_data TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    steps_completed TEXT NOT NULL
);
```

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Workflow**:
   Create a YAML file in `workflows/` directory

3. **Test Workflow**:
   ```bash
   python test_dmv_workflow.py
   ```

4. **Start Server**:
   ```bash
   python server.py
   ```

## Extending the System

### Adding New Tools

1. Add tool execution logic to appropriate `execute_*_tool()` function
2. Update workflow YAML to use new tool
3. Test with sample data

### Adding New MCPs

1. Add new execution function (e.g., `execute_social_tool()`)
2. Update tool routing in `execute_tool()`
3. Add tool definitions to workflows

### Creating Workflows

1. Create YAML file in `workflows/` directory
2. Define triggers, conditions, and steps
3. Test with sample trigger data
4. Deploy and monitor execution

## Production Deployment

For production use:

1. **HTTP API**: Add REST API for workflow triggering
2. **Authentication**: Secure MCP server communications
3. **Monitoring**: Add workflow execution dashboards
4. **Scaling**: Implement async task queues
5. **Testing**: Create comprehensive test suite

## Example Workflows

The system includes several example workflows:

- `dmv_document_processing.yml`: Government notice processing
- `invoice_processing.yml`: Invoice → QuickBooks automation
- `legal_notice_processing.yml`: Legal document handling
- `customer_communication.yml`: Customer service automation

## Troubleshooting

- Check workflow YAML syntax
- Verify MCP server connectivity
- Review execution logs in database
- Test individual tools separately
- Validate parameter resolution

This workflow system provides the foundation for automating hundreds of business processes across your MCP ecosystem.