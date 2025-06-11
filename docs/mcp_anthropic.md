Set up Model Context Protocol (MCP)
Model Context Protocol (MCP) is an open protocol that enables LLMs to access external tools and data sources. For more details, see the MCP documentation.

Use third party MCP servers at your own risk. Make sure you trust the MCP servers, and be especially careful when using MCP servers that talk to the internet, as these can expose you to prompt injection risk.

​
Configure MCP servers
When to use: You want to enhance Claude’s capabilities by connecting it to specialized tools and external servers using the Model Context Protocol.

1
Add an MCP Stdio Server


Copy
# Basic syntax
claude mcp add <name> <command> [args...]

# Example: Adding a local server
claude mcp add my-server -e API_KEY=123 -- /path/to/server arg1 arg2
2
Add an MCP SSE Server


Copy
# Basic syntax
claude mcp add --transport sse <name> <url>

# Example: Adding an SSE server
claude mcp add --transport sse sse-server https://example.com/sse-endpoint
3
Manage your MCP servers


Copy
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get my-server

# Remove a server
claude mcp remove my-server
Tips:

Use the -s or --scope flag to specify where the configuration is stored:
local (default): Available only to you in the current project (was called project in older versions)
project: Shared with everyone in the project via .mcp.json file
user: Available to you across all projects (was called global in older versions)
Set environment variables with -e or --env flags (e.g., -e KEY=value)
Configure MCP server startup timeout using the MCP_TIMEOUT environment variable (e.g., MCP_TIMEOUT=10000 claude sets a 10-second timeout)
Check MCP server status any time using the /mcp command within Claude Code
MCP follows a client-server architecture where Claude Code (the client) can connect to multiple specialized servers
​
Understanding MCP server scopes
When to use: You want to understand how different MCP scopes work and how to share servers with your team.

1
Local-scoped MCP servers

The default scope (local) stores MCP server configurations in your project-specific user settings. These servers are only available to you while working in the current project.


Copy
# Add a local-scoped server (default)
claude mcp add my-private-server /path/to/server

# Explicitly specify local scope
claude mcp add my-private-server -s local /path/to/server
2
Project-scoped MCP servers (.mcp.json)

Project-scoped servers are stored in a .mcp.json file at the root of your project. This file should be checked into version control to share servers with your team.


Copy
# Add a project-scoped server
claude mcp add shared-server -s project /path/to/server
This creates or updates a .mcp.json file with the following structure:


Copy
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
3
User-scoped MCP servers

User-scoped servers are available to you across all projects on your machine, and are private to you.


Copy
# Add a user server
claude mcp add my-user-server -s user /path/to/server
Tips:

Local-scoped servers take precedence over project-scoped and user-scoped servers with the same name
Project-scoped servers (in .mcp.json) take precedence over user-scoped servers with the same name
Before using project-scoped servers from .mcp.json, Claude Code will prompt you to approve them for security
The .mcp.json file is intended to be checked into version control to share MCP servers with your team
Project-scoped servers make it easy to ensure everyone on your team has access to the same MCP tools
If you need to reset your choices for which project-scoped servers are enabled or disabled, use the claude mcp reset-project-choices command