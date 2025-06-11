# Claude MCP Servers

This project demonstrates the integration of Model Context Protocol (MCP) servers with Claude Desktop.

## Available MCP Servers

### 1. Fetch MCP Server

The MCP Fetch server provides web content fetching capabilities, enabling Claude to retrieve and process content from web pages.

```json
"fetch": {
  "command": "node",
  "args": ["/Users/andrew/Projects/claudecode1/src/fetch/server.js"]
}
```

### 2. Playwright MCP Server

The Playwright MCP server enables browser automation capabilities, allowing Claude to interact with web pages.

```json
"playwright": {
  "command": "npx",
  "args": ["@playwright/mcp@latest", "--config", "/Users/andrew/Projects/claudecode1/src/playwright/config/playwright-mcp-config.json"]
}
```

### 3. Vision OpenAI MCP

A document processing service that uses OpenAI's Vision models to analyze images and PDFs, with special handling for invoices.

```json
"vision": {
  "type": "stdio",
  "command": "python",
  "args": ["/Users/andrew/Projects/claudecode1/src/vision-openai-mcp/server.py"]
}
```

### 4. CRM Database MCP Server

A comprehensive CRM system with contact management, communication processing (email, iMessage, WhatsApp, etc.), and financial tracking. Designed specifically for Claude Code with LLM-optimized tools and resources.

**Features**:
- Universal communication tracking (email, SMS, WhatsApp, iMessage, Instagram DMs, physical mail)
- Contact and company relationship management  
- Financial tracking (accounts, transactions, subscriptions)
- Task management and follow-up automation
- Cross-platform identity resolution
- AI-ready data structure with built-in processing fields

```json
"crm-db": {
  "command": "python3",
  "args": ["/Users/andrew/Projects/claudecode1/src/crm-db/server.py"],
  "env": {
    "CRM_DB_PATH": "/Users/andrew/Projects/claudecode1/src/crm-db/crm.db"
  }
}
```

## Setup Vision OpenAI MCP

1. Install dependencies:
   ```bash
   pip install "mcp[cli]" httpx python-dotenv pdf2image Pillow
   ```

2. Set your OpenAI API Key:
   ```bash
   cd src/vision-openai-mcp
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

3. Use the server in Claude Desktop by adding it to your configuration.

## Setup CRM Database MCP

1. Install dependencies:
   ```bash
   cd src/crm-db
   pip install -r requirements.txt
   ```

2. Initialize database:
   ```bash
   python database.py --init --sample-data
   ```

3. Test the server:
   ```bash
   python test_server.py
   ```

4. The server is automatically available in Claude Code via the `mcp.json` configuration.

## Running the Servers

You can run the servers directly using the scripts in package.json:

```bash
# Run Fetch MCP
npm run mcp-fetch

# Run Playwright MCP
npm run mcp-playwright
```

For the Vision MCP, you can run it with:

```bash
python src/vision-openai-mcp/server.py
```

For the CRM Database MCP:

```bash
python3 src/crm-db/server.py
```

**Note**: The CRM server is designed for use with Claude Code and will be automatically started when Claude Code initializes the MCP servers.

## Requirements

- **Claude Code** (for CRM MCP Server)
- Claude Desktop (for other servers)
- Python 3.8+ with dependencies
- Node.js and npm for Playwright MCP
- OpenAI API key for Vision MCP

## Documentation

For more detailed information about each MCP server, see the individual READMEs in their respective directories:
- [Fetch MCP](src/fetch/README.md)
- [Vision OpenAI MCP](src/vision-openai-mcp/README.md)
- [CRM Database MCP](src/crm-db/README.md)
- [CRM Database Schema Documentation](docs/crm_database_schema.md)

### CRM Database MCP Additional Guides
- [Testing Guide](src/crm-db/TESTING.md) - Comprehensive testing instructions
- [Claude Code Usage Guide](src/crm-db/CLAUDE_CODE_USAGE.md) - How to use with Claude Code