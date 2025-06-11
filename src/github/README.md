# GitHub MCP Server

A comprehensive GitHub integration MCP server that provides access to GitHub API functionality through the Model Context Protocol.

## Features

### Repository Management
- List repositories (user/organization)
- Get repository details
- Create new repositories
- Fork repositories

### Issue Management
- List issues with filters
- Create new issues
- Get issue details
- Update existing issues
- Add comments to issues

### Pull Request Operations
- List pull requests
- Create new pull requests
- Get pull request details
- Merge pull requests

### File Operations
- Read file contents
- Create/update single files
- Push multiple files in one commit

### Search Capabilities
- Search repositories
- Search code across repositories
- Search issues and pull requests
- Search users

### Additional Features
- Branch creation
- Commit history
- GitHub authentication

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up GitHub Personal Access Token in `.env` file:
```bash
cd /path/to/src/github
cp .env.example .env
# Edit .env and add your token:
# GITHUB_TOKEN=ghp_your_token_here
```

3. Add to your MCP configuration (`mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["/path/to/src/github/server.py"]
    }
  }
}
```

## Usage

Once configured, the GitHub MCP server provides the following tools:

### Authentication
- `github_authenticate` - Set GitHub personal access token

### Repository Tools
- `github_list_repos` - List repositories
- `github_get_repo` - Get repository details
- `github_create_repo` - Create new repository
- `github_fork_repo` - Fork a repository

### Issue Tools
- `github_list_issues` - List issues with filters
- `github_create_issue` - Create new issue
- `github_get_issue` - Get issue details
- `github_update_issue` - Update existing issue
- `github_add_issue_comment` - Add comment to issue

### Pull Request Tools
- `github_list_prs` - List pull requests
- `github_create_pr` - Create new pull request
- `github_get_pr` - Get pull request details
- `github_merge_pr` - Merge pull request

### File Tools
- `github_get_file` - Get file contents
- `github_push_file` - Create/update single file
- `github_push_files` - Push multiple files

### Search Tools
- `github_search_repos` - Search repositories
- `github_search_code` - Search code
- `github_search_issues` - Search issues/PRs
- `github_search_users` - Search users

### Other Tools
- `github_create_branch` - Create new branch
- `github_list_commits` - List commits

## Authentication

The server requires a GitHub Personal Access Token with appropriate scopes:
- `repo` - Full control of private repositories
- `user` - Read user profile data
- `read:org` - Read org and team membership (if accessing org repos)

## Error Handling

The server includes comprehensive error handling:
- Authentication failures
- Rate limiting
- API errors
- Network issues

All errors are logged and returned with descriptive messages.

## Examples

### List repositories
```python
result = github_list_repos(owner="octocat", type="all", sort="updated")
```

### Create an issue
```python
result = github_create_issue(
    owner="myorg",
    repo="myrepo",
    title="Bug: Application crashes on startup",
    body="Detailed description here",
    labels=["bug", "high-priority"]
)
```

### Search for code
```python
result = github_search_code(
    query="language:python filename:setup.py",
    sort="indexed"
)
```

## Development

To run the server in standalone mode:
```bash
python server.py
```

For development with MCP Inspector:
```bash
mcp dev server.py
```

## License

This MCP server follows the same license as the parent project.