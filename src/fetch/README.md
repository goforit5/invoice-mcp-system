# Fetch MCP for Claude

A Model Context Protocol (MCP) server for fetching web content, allowing Claude to retrieve and process information from websites.

## Features

- Fetch web content from URLs
- Support for chunking large content (start index and max length)
- Basic HTML to Markdown conversion
- JSON and raw content support
- 15-minute content caching for better performance
- HTTPS upgrade for security
- Compatible with Cursor's MCP protocol

## Usage

### Starting the Server

```bash
npm run mcp-fetch
```

### Configuring in Cursor

Add the following to your Cursor MCP configuration:

```json
"fetch": {
  "command": "node",
  "args": ["/path/to/claudecode1/src/fetch/server.js"]
}
```

### Tool Parameters

The fetchUrl tool accepts the following parameters:

- `url` (required): The URL to fetch content from
- `maxLength` (optional): Maximum length of content to return (default: 15000)
- `startIndex` (optional): Index to start from for paginated fetching (default: 0)
- `raw` (optional): Return raw content without HTML to Markdown conversion (default: false)

### Response Format

```json
{
  "content": "Fetched content...",
  "contentType": "text/html; charset=utf-8",
  "truncated": false,
  "startIndex": 0,
  "length": 12345
}
```

## Integration with Claude

In Claude or Cursor, you can use the fetch functionality with prompts like:

```
Use the fetchUrl tool to retrieve the content from https://example.com
```

For paginated fetching:
```
Use the fetchUrl tool to retrieve the content from https://example.com with startIndex=15000
```

For raw content:
```
Use the fetchUrl tool to retrieve the content from https://example.com with raw=true
```

## Best Practices

1. Start with 15,000-character chunks
2. Check if content is truncated to determine if you need more chunks
3. Use startIndex parameter for paginated fetching
4. For JSON data, use raw=true parameter to avoid conversion
5. For large JSON, use pagination to retrieve the complete structure

## MCP Protocol Implementation

This server implements the Model Context Protocol (MCP) standard which allows it to be used with Cursor and other MCP-compatible clients. The implementation:

1. Uses stdio communication instead of HTTP
2. Registers the `fetchUrl` tool with the MCP server
3. Handles parameters according to MCP conventions
4. Returns structured responses compatible with MCP clients