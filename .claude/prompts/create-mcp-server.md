# AI Expert MCP Server Creator

Become an expert MCP (Model Context Protocol) server developer who can autonomously create complete, production-ready MCP servers from a single command like "create new mcp server for github". 

## System Intelligence & Auto-Discovery

**CRITICAL**: Execute this comprehensive analysis sequence automatically before creating any MCP server:

### Phase 1: Project Context Analysis
1. **Read Project Configuration**:
   - `mcp.json` - Current MCP server configurations and patterns
   - `CLAUDE.md` - Project conventions and requirements
   - `README.md` - System architecture understanding
   - `package.json` - Dependencies and scripts
   - `.gitignore` - File patterns to exclude

2. **Read MCP Documentation & Guidelines**:
   - `docs/mcp_anthropic.md` - Claude Code MCP configuration, scopes, and CLI commands
   - `docs/mcp-python-sdk.mdc` - FastMCP framework patterns, best practices, and examples
   
3. **Analyze Existing MCP Servers** (Read ALL files in each directory):
   - `src/vision/` - OpenAI integration patterns, error handling, cost tracking
   - `src/quickbooks/` - OAuth flows, API integration, business logic
   - `src/crm-db/` - Database operations, FastMCP usage, security patterns
   - `src/fetch/` - Web content retrieval, response formatting
   - `src/playwright/` - Browser automation patterns

4. **Extract Implementation Patterns**:
   - **File Structure**: `server.py`, `index.py`, `requirements.txt`, `README.md`
   - **Framework Preference**: FastMCP for Python servers
   - **Error Handling**: Try/catch with logging, graceful fallbacks
   - **Authentication**: OAuth patterns, credential storage, token refresh
   - **Cost Tracking**: Token usage monitoring, pricing calculations
   - **Output Formatting**: Structured JSON responses, file saving patterns
   - **Configuration**: Environment variables, config files
   - **Documentation**: Comprehensive tool descriptions, usage examples

### Phase 2: External Research & Best Practices
4. **MCP Official Documentation Research**:
   ```bash
   # Fetch current MCP documentation
   WebFetch("https://modelcontextprotocol.io", "Get latest MCP server creation guidelines, best practices, and tool patterns")
   WebFetch("https://github.com/modelcontextprotocol", "Find example implementations and SDK patterns")
   ```

5. **Target Service API Research** (Example: GitHub):
   ```bash
   # Research target service capabilities
   WebFetch("https://docs.github.com/en/rest", "Understand GitHub API capabilities, authentication methods, and common operations")
   WebFetch("https://github.com/PyGithub/PyGithub", "Review Python GitHub SDK patterns and examples")
   ```

### Phase 3: Automated Implementation

## MCP Server Creation Template

Based on analysis, create production-ready MCP server with this structure:

```
src/{service_name}/
├── server.py           # FastMCP server with all tools
├── index.py           # Core business logic and API integration  
├── requirements.txt   # Dependencies with version pinning
├── README.md         # Usage guide and tool documentation
├── config_template.json  # Configuration template
└── templates/        # Any JSON templates needed
    └── {service}_template.json
```

### Core Server Implementation (server.py)

```python
#!/Users/andrew/Projects/claudecode1/vision-mcp-env/bin/python3
"""
MCP server for {SERVICE} functionality - {DESCRIPTION}
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from index import (
    # Import all core functions
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("{SERVICE} MCP")

@mcp.tool()
def {primary_operation}(param1: str, param2: int = None) -> dict:
    """
    Primary tool description with comprehensive details
    
    Args:
        param1: Required parameter description
        param2: Optional parameter with default
    
    Returns:
        Structured JSON response with operation results
    """
    try:
        logger.info(f"Starting {primary_operation} operation...")
        result = core_function(param1, param2)
        logger.info(f"Operation completed successfully")
        return result
    except Exception as error:
        logger.error(f"Error in {primary_operation}: {error}")
        raise Exception(f"Failed to execute {primary_operation}: {str(error)}")

# Additional tools following same pattern...

@mcp.resource("{service}://about")
def get_about() -> str:
    """Information about the {SERVICE} MCP server"""
    return """
{SERVICE} MCP Server
--------------------
A comprehensive {SERVICE} integration service that enables:
- [List key capabilities]
- [Authentication and security features]
- [Data processing capabilities]

Available tools:
- '{tool1}': Description
- '{tool2}': Description

Integration notes:
[Any special integration requirements or patterns]
"""

if __name__ == "__main__":
    logger.info("Starting {SERVICE} MCP server...")
    mcp.run()
```

### Business Logic Implementation (index.py)

```python
"""
{SERVICE} integration core functionality
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import service-specific SDKs
from {service_sdk} import {ServiceClient}

# Configure logging
logger = logging.getLogger(__name__)

def authenticate_{service}(credentials: Dict) -> Dict:
    """Handle authentication with proper token management"""
    pass

def core_operation(param1: str, param2: int = None) -> Dict:
    """Main business logic with error handling and logging"""
    pass

# Additional core functions...
```

### Dependencies (requirements.txt)

```
mcp[cli]>=1.0.0
{service_specific_sdk}
requests>=2.31.0
python-dotenv>=1.0.0
# Add other dependencies based on service requirements
```

### Documentation (README.md)

```markdown
# {SERVICE} MCP Server

{SERVICE} integration for automated [functionality description].

## Features
- [Key feature 1]
- [Key feature 2]  
- [Authentication support]

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure authentication: [specific steps]
3. Test server: `python server.py`

## Available Tools
### `{tool1}`
Description and usage examples

### `{tool2}` 
Description and usage examples

## Configuration
[Environment variables and config file details]

## Integration with Claude Code
[How to use in workflows]
```

## Automated Implementation Process

When user requests "create new mcp server for {service}":

1. **Auto-analyze existing patterns** (read all existing MCP servers)
2. **Research target service** (fetch API docs, SDK examples)
3. **Generate server structure** following established patterns
4. **Implement authentication** using service-specific methods
5. **Create comprehensive tools** covering main service operations
6. **Add to mcp.json configuration** automatically
7. **Execute Claude Code registration commands**:
   ```bash
   # Register the new MCP server with Claude Code
   claude mcp add {service_name} -s project /Users/andrew/Projects/claudecode1/src/{service}/server.py
   
   # Add environment variables if needed
   claude mcp add {service_name} -s project -e API_KEY=placeholder -e CONFIG_PATH=./config /Users/andrew/Projects/claudecode1/src/{service}/server.py
   
   # Verify registration
   claude mcp list
   ```
8. **Test server functionality** with basic operations
9. **Verify integration** with `claude mcp get {service_name}`
10. **Generate documentation** with examples

### Claude Code Integration Steps

**CRITICAL**: After creating the MCP server, automatically register it with Claude Code:

```bash
# Choose appropriate scope based on server type:
# - project: Shared with team (add to .mcp.json) 
# - local: Personal use only
# - user: Available across all projects

# For team-shared servers (recommended for project MCP servers):
claude mcp add {service_name} -s project {path_to_server} {args}

# Add environment variables if needed:
claude mcp add {service_name} -s project -e API_KEY=placeholder -e CONFIG_PATH=./config {path_to_server}

# Verify registration:
claude mcp list

# Test server status:
claude mcp get {service_name}
```

**Configuration Pattern**:
- **Project Scope**: For servers that should be shared with the team
- **Environment Variables**: Use `-e` flag for API keys and configuration
- **Path**: Use absolute path to server.py file
- **Arguments**: Include any required command line arguments

**Post-Registration**:
1. Update `.mcp.json` if using project scope
2. Create `.env.example` file with required environment variables
3. Document configuration steps in server README.md
4. Test server connectivity with `claude mcp list` and verify tools are available

## Quality Standards

Every generated MCP server must include:

✅ **Security**: Proper credential handling, input validation  
✅ **Error Handling**: Comprehensive try/catch with meaningful messages  
✅ **Logging**: Detailed operation tracking for debugging  
✅ **Documentation**: Complete tool descriptions and usage examples  
✅ **Testing**: Basic functionality verification  
✅ **Integration**: Seamless addition to existing Claude Code setup  
✅ **Performance**: Efficient API usage and response handling  
✅ **Extensibility**: Clean architecture for future enhancements  

## Service-Specific Implementation Guides

### GitHub MCP Server
- **Authentication**: GitHub App, Personal Access Token, OAuth flows
- **Core Tools**: Repository management, issue tracking, code search, PR operations
- **Special Features**: Webhook handling, GitHub Actions integration
- **SDK**: PyGithub or github3.py

### Slack MCP Server  
- **Authentication**: Bot tokens, OAuth scopes
- **Core Tools**: Message sending, channel management, user lookup
- **Special Features**: Real-time messaging, file uploads
- **SDK**: slack-sdk

### Gmail MCP Server
- **Authentication**: OAuth 2.0, service accounts
- **Core Tools**: Email sending, reading, search, label management  
- **Special Features**: Attachment handling, thread management
- **SDK**: google-api-python-client

### Twitter/X MCP Server
- **Authentication**: API v2 bearer tokens, OAuth 1.0a
- **Core Tools**: Tweet posting, timeline reading, user management
- **Special Features**: Media upload, streaming API
- **SDK**: tweepy

## Advanced Features

### Multi-Service Integration
- Cross-reference data between services
- Unified authentication management
- Shared caching and rate limiting

### AI-Enhanced Operations
- Intelligent content generation
- Automated workflow suggestions  
- Context-aware API usage

### Enterprise Features
- Team authentication management
- Usage analytics and reporting
- Custom compliance controls

## Success Criteria

A successful MCP server creation includes:

1. **Immediate Functionality**: Server starts and responds to basic operations
2. **Complete Tool Set**: All major service operations covered
3. **Production Ready**: Error handling, logging, security implemented  
4. **Well Documented**: Clear usage instructions and examples
5. **Integrated**: Added to Claude Code configuration automatically
6. **Tested**: Basic operations verified and working

## Usage Pattern

```bash
# User Command
"create new mcp server for github"

# Expected Result  
✅ New GitHub MCP server created in src/github/
✅ All tools implemented (repos, issues, PRs, etc.)  
✅ Authentication configured
✅ Added to mcp.json
✅ Registered with Claude Code (project scope)
✅ Environment variables documented
✅ Documentation generated
✅ Basic tests passed
✅ Server status verified with `claude mcp list`
✅ Ready for immediate use in Claude Code
```

## Implementation Checklist

For every MCP server creation, verify:

**📁 File Structure**:
- [ ] `src/{service}/server.py` - FastMCP server with comprehensive tools
- [ ] `src/{service}/index.py` - Core business logic and API integration
- [ ] `src/{service}/requirements.txt` - All dependencies with versions
- [ ] `src/{service}/README.md` - Complete usage documentation
- [ ] `src/{service}/.env.example` - Environment variable template

**🔧 Configuration**:
- [ ] Updated `mcp.json` with new server entry
- [ ] Registered with Claude Code using `claude mcp add`
- [ ] Environment variables properly documented
- [ ] Authentication flow implemented and tested

**🛠️ Functionality**:
- [ ] All major service operations covered as tools
- [ ] Proper error handling with meaningful messages
- [ ] Comprehensive logging for debugging
- [ ] Input validation and security measures
- [ ] Graceful fallbacks for API failures

**📚 Documentation**:
- [ ] Tool descriptions with clear parameters
- [ ] Usage examples for each tool
- [ ] Authentication setup instructions
- [ ] Integration notes for Claude Code workflows
- [ ] Troubleshooting guide

**✅ Verification**:
- [ ] Server starts without errors: `python src/{service}/server.py`
- [ ] Shows in MCP list: `claude mcp list`
- [ ] Tools are discoverable in Claude Code
- [ ] Basic operations tested and working
- [ ] Authentication flow verified

Transform into an expert MCP server developer who can autonomously create complete, production-ready MCP servers following these comprehensive guidelines.