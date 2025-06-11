#!/Users/andrew/Projects/claudecode1/vision-mcp-env/bin/python3
"""
MCP server for GitHub functionality - GitHub API integration for repository, issue, and PR management
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from index import (
    authenticate_github,
    list_repositories,
    get_repository,
    create_repository,
    list_issues,
    create_issue,
    get_issue,
    update_issue,
    add_issue_comment,
    list_pull_requests,
    create_pull_request,
    get_pull_request,
    merge_pull_request,
    get_file_contents,
    create_or_update_file,
    push_files,
    search_repositories,
    search_code,
    search_issues,
    search_users,
    fork_repository,
    create_branch,
    list_commits
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("GitHub MCP")

@mcp.tool()
def github_authenticate(token: str) -> dict:
    """
    Authenticate with GitHub using personal access token
    
    Args:
        token: GitHub personal access token
    
    Returns:
        Authentication status and user information
    """
    try:
        logger.info("Authenticating with GitHub...")
        result = authenticate_github(token)
        logger.info("GitHub authentication successful")
        return result
    except Exception as error:
        logger.error(f"Error in github_authenticate: {error}")
        raise Exception(f"Failed to authenticate with GitHub: {str(error)}")

@mcp.tool()
def github_list_repos(owner: str = None, type: str = "all", sort: str = "updated", per_page: int = 30) -> dict:
    """
    List GitHub repositories for authenticated user or specified owner
    
    Args:
        owner: Repository owner (username or organization). If None, lists authenticated user's repos
        type: Repository type (all, owner, public, private, member)
        sort: Sort order (created, updated, pushed, full_name)
        per_page: Number of results per page (max 100)
    
    Returns:
        List of repositories with details
    """
    try:
        logger.info(f"Listing repositories for owner: {owner or 'authenticated user'}")
        result = list_repositories(owner, type, sort, per_page)
        logger.info(f"Found {len(result.get('repositories', []))} repositories")
        return result
    except Exception as error:
        logger.error(f"Error in github_list_repos: {error}")
        raise Exception(f"Failed to list repositories: {str(error)}")

@mcp.tool()
def github_get_repo(owner: str, repo: str) -> dict:
    """
    Get detailed information about a specific repository
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    
    Returns:
        Repository details including stats, topics, and metadata
    """
    try:
        logger.info(f"Getting repository details for {owner}/{repo}")
        result = get_repository(owner, repo)
        logger.info("Repository details retrieved successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_get_repo: {error}")
        raise Exception(f"Failed to get repository {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_create_repo(name: str, description: str = None, private: bool = False, auto_init: bool = True) -> dict:
    """
    Create a new GitHub repository
    
    Args:
        name: Repository name
        description: Repository description
        private: Whether repository should be private
        auto_init: Initialize repository with README
    
    Returns:
        Created repository details
    """
    try:
        logger.info(f"Creating repository: {name}")
        result = create_repository(name, description, private, auto_init)
        logger.info(f"Repository {name} created successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_create_repo: {error}")
        raise Exception(f"Failed to create repository {name}: {str(error)}")

@mcp.tool()
def github_list_issues(owner: str, repo: str, state: str = "open", labels: str = None, assignee: str = None, per_page: int = 30) -> dict:
    """
    List issues in a repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: Issue state (open, closed, all)
        labels: Comma-separated list of labels to filter by
        assignee: Username to filter issues by assignee
        per_page: Number of results per page (max 100)
    
    Returns:
        List of issues with details
    """
    try:
        logger.info(f"Listing issues for {owner}/{repo}")
        result = list_issues(owner, repo, state, labels, assignee, per_page)
        logger.info(f"Found {len(result.get('issues', []))} issues")
        return result
    except Exception as error:
        logger.error(f"Error in github_list_issues: {error}")
        raise Exception(f"Failed to list issues for {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_create_issue(owner: str, repo: str, title: str, body: str = None, assignees: list = None, labels: list = None) -> dict:
    """
    Create a new issue in a repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        title: Issue title
        body: Issue description
        assignees: List of usernames to assign
        labels: List of labels to apply
    
    Returns:
        Created issue details
    """
    try:
        logger.info(f"Creating issue in {owner}/{repo}: {title}")
        result = create_issue(owner, repo, title, body, assignees, labels)
        logger.info(f"Issue #{result.get('number')} created successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_create_issue: {error}")
        raise Exception(f"Failed to create issue in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_get_issue(owner: str, repo: str, issue_number: int) -> dict:
    """
    Get details of a specific issue
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
    
    Returns:
        Issue details including comments and timeline
    """
    try:
        logger.info(f"Getting issue #{issue_number} from {owner}/{repo}")
        result = get_issue(owner, repo, issue_number)
        logger.info("Issue details retrieved successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_get_issue: {error}")
        raise Exception(f"Failed to get issue #{issue_number} from {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_update_issue(owner: str, repo: str, issue_number: int, title: str = None, body: str = None, state: str = None, assignees: list = None, labels: list = None) -> dict:
    """
    Update an existing issue
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        title: New issue title
        body: New issue description
        state: New issue state (open, closed)
        assignees: List of usernames to assign
        labels: List of labels to apply
    
    Returns:
        Updated issue details
    """
    try:
        logger.info(f"Updating issue #{issue_number} in {owner}/{repo}")
        result = update_issue(owner, repo, issue_number, title, body, state, assignees, labels)
        logger.info("Issue updated successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_update_issue: {error}")
        raise Exception(f"Failed to update issue #{issue_number} in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> dict:
    """
    Add a comment to an issue
    
    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        body: Comment text
    
    Returns:
        Created comment details
    """
    try:
        logger.info(f"Adding comment to issue #{issue_number} in {owner}/{repo}")
        result = add_issue_comment(owner, repo, issue_number, body)
        logger.info("Comment added successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_add_issue_comment: {error}")
        raise Exception(f"Failed to add comment to issue #{issue_number} in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_list_prs(owner: str, repo: str, state: str = "open", head: str = None, base: str = None, per_page: int = 30) -> dict:
    """
    List pull requests in a repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: PR state (open, closed, all)
        head: Filter by head branch (user:branch-name)
        base: Filter by base branch
        per_page: Number of results per page (max 100)
    
    Returns:
        List of pull requests with details
    """
    try:
        logger.info(f"Listing pull requests for {owner}/{repo}")
        result = list_pull_requests(owner, repo, state, head, base, per_page)
        logger.info(f"Found {len(result.get('pull_requests', []))} pull requests")
        return result
    except Exception as error:
        logger.error(f"Error in github_list_prs: {error}")
        raise Exception(f"Failed to list pull requests for {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_create_pr(owner: str, repo: str, title: str, head: str, base: str, body: str = None, draft: bool = False) -> dict:
    """
    Create a new pull request
    
    Args:
        owner: Repository owner
        repo: Repository name
        title: Pull request title
        head: The branch containing changes (user:branch-name)
        base: The branch you want changes merged into
        body: Pull request description
        draft: Whether to create as draft PR
    
    Returns:
        Created pull request details
    """
    try:
        logger.info(f"Creating pull request in {owner}/{repo}: {title}")
        result = create_pull_request(owner, repo, title, head, base, body, draft)
        logger.info(f"Pull request #{result.get('number')} created successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_create_pr: {error}")
        raise Exception(f"Failed to create pull request in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_get_pr(owner: str, repo: str, pull_number: int) -> dict:
    """
    Get details of a specific pull request
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
    
    Returns:
        Pull request details including files and status
    """
    try:
        logger.info(f"Getting pull request #{pull_number} from {owner}/{repo}")
        result = get_pull_request(owner, repo, pull_number)
        logger.info("Pull request details retrieved successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_get_pr: {error}")
        raise Exception(f"Failed to get pull request #{pull_number} from {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_merge_pr(owner: str, repo: str, pull_number: int, commit_title: str = None, commit_message: str = None, merge_method: str = "merge") -> dict:
    """
    Merge a pull request
    
    Args:
        owner: Repository owner
        repo: Repository name
        pull_number: Pull request number
        commit_title: Title for merge commit
        commit_message: Message for merge commit
        merge_method: Merge method (merge, squash, rebase)
    
    Returns:
        Merge result details
    """
    try:
        logger.info(f"Merging pull request #{pull_number} in {owner}/{repo}")
        result = merge_pull_request(owner, repo, pull_number, commit_title, commit_message, merge_method)
        logger.info("Pull request merged successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_merge_pr: {error}")
        raise Exception(f"Failed to merge pull request #{pull_number} in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_get_file(owner: str, repo: str, path: str, branch: str = None) -> dict:
    """
    Get contents of a file from repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: File path in repository
        branch: Branch name (defaults to default branch)
    
    Returns:
        File contents and metadata
    """
    try:
        logger.info(f"Getting file {path} from {owner}/{repo}")
        result = get_file_contents(owner, repo, path, branch)
        logger.info("File contents retrieved successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_get_file: {error}")
        raise Exception(f"Failed to get file {path} from {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_push_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = None, sha: str = None) -> dict:
    """
    Create or update a file in repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: File path in repository
        content: File content (base64 encoded for binary files)
        message: Commit message
        branch: Branch name (defaults to default branch)
        sha: SHA of file being replaced (required for updates)
    
    Returns:
        Commit details
    """
    try:
        logger.info(f"Pushing file {path} to {owner}/{repo}")
        result = create_or_update_file(owner, repo, path, content, message, branch, sha)
        logger.info("File pushed successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_push_file: {error}")
        raise Exception(f"Failed to push file {path} to {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_push_files(owner: str, repo: str, files: list, message: str, branch: str = None) -> dict:
    """
    Push multiple files to repository in single commit
    
    Args:
        owner: Repository owner
        repo: Repository name
        files: List of files [{"path": "file.txt", "content": "content"}]
        message: Commit message
        branch: Branch name (defaults to default branch)
    
    Returns:
        Commit details
    """
    try:
        logger.info(f"Pushing {len(files)} files to {owner}/{repo}")
        result = push_files(owner, repo, files, message, branch)
        logger.info("Files pushed successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_push_files: {error}")
        raise Exception(f"Failed to push files to {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_search_repos(query: str, sort: str = "stars", order: str = "desc", per_page: int = 30) -> dict:
    """
    Search GitHub repositories
    
    Args:
        query: Search query (supports GitHub search syntax)
        sort: Sort field (stars, forks, help-wanted-issues, updated)
        order: Sort order (asc, desc)
        per_page: Number of results per page (max 100)
    
    Returns:
        Search results with repository details
    """
    try:
        logger.info(f"Searching repositories: {query}")
        result = search_repositories(query, sort, order, per_page)
        logger.info(f"Found {result.get('total_count', 0)} repositories")
        return result
    except Exception as error:
        logger.error(f"Error in github_search_repos: {error}")
        raise Exception(f"Failed to search repositories: {str(error)}")

@mcp.tool()
def github_search_code(query: str, sort: str = None, order: str = "desc", per_page: int = 30) -> dict:
    """
    Search code across GitHub repositories
    
    Args:
        query: Search query (supports GitHub code search syntax)
        sort: Sort field (indexed)
        order: Sort order (asc, desc)
        per_page: Number of results per page (max 100)
    
    Returns:
        Code search results
    """
    try:
        logger.info(f"Searching code: {query}")
        result = search_code(query, sort, order, per_page)
        logger.info(f"Found {result.get('total_count', 0)} code results")
        return result
    except Exception as error:
        logger.error(f"Error in github_search_code: {error}")
        raise Exception(f"Failed to search code: {str(error)}")

@mcp.tool()
def github_search_issues(query: str, sort: str = "created", order: str = "desc", per_page: int = 30) -> dict:
    """
    Search issues and pull requests across GitHub
    
    Args:
        query: Search query (supports GitHub search syntax)
        sort: Sort field (comments, reactions, created, updated)
        order: Sort order (asc, desc)
        per_page: Number of results per page (max 100)
    
    Returns:
        Issue/PR search results
    """
    try:
        logger.info(f"Searching issues: {query}")
        result = search_issues(query, sort, order, per_page)
        logger.info(f"Found {result.get('total_count', 0)} issues/PRs")
        return result
    except Exception as error:
        logger.error(f"Error in github_search_issues: {error}")
        raise Exception(f"Failed to search issues: {str(error)}")

@mcp.tool()
def github_search_users(query: str, sort: str = "joined", order: str = "desc", per_page: int = 30) -> dict:
    """
    Search GitHub users
    
    Args:
        query: Search query
        sort: Sort field (followers, repositories, joined)
        order: Sort order (asc, desc)
        per_page: Number of results per page (max 100)
    
    Returns:
        User search results
    """
    try:
        logger.info(f"Searching users: {query}")
        result = search_users(query, sort, order, per_page)
        logger.info(f"Found {result.get('total_count', 0)} users")
        return result
    except Exception as error:
        logger.error(f"Error in github_search_users: {error}")
        raise Exception(f"Failed to search users: {str(error)}")

@mcp.tool()
def github_fork_repo(owner: str, repo: str, organization: str = None) -> dict:
    """
    Fork a repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        organization: Organization to fork to (optional)
    
    Returns:
        Forked repository details
    """
    try:
        logger.info(f"Forking repository {owner}/{repo}")
        result = fork_repository(owner, repo, organization)
        logger.info("Repository forked successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_fork_repo: {error}")
        raise Exception(f"Failed to fork repository {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_create_branch(owner: str, repo: str, branch: str, from_branch: str = None) -> dict:
    """
    Create a new branch
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: New branch name
        from_branch: Source branch (defaults to default branch)
    
    Returns:
        Created branch details
    """
    try:
        logger.info(f"Creating branch {branch} in {owner}/{repo}")
        result = create_branch(owner, repo, branch, from_branch)
        logger.info("Branch created successfully")
        return result
    except Exception as error:
        logger.error(f"Error in github_create_branch: {error}")
        raise Exception(f"Failed to create branch {branch} in {owner}/{repo}: {str(error)}")

@mcp.tool()
def github_list_commits(owner: str, repo: str, sha: str = None, path: str = None, per_page: int = 30) -> dict:
    """
    List commits in a repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        sha: SHA or branch to start listing commits from
        path: File path to filter commits
        per_page: Number of results per page (max 100)
    
    Returns:
        List of commits with details
    """
    try:
        logger.info(f"Listing commits for {owner}/{repo}")
        result = list_commits(owner, repo, sha, path, per_page)
        logger.info(f"Found {len(result.get('commits', []))} commits")
        return result
    except Exception as error:
        logger.error(f"Error in github_list_commits: {error}")
        raise Exception(f"Failed to list commits for {owner}/{repo}: {str(error)}")

@mcp.resource("github://about")
def get_about() -> str:
    """Information about the GitHub MCP server"""
    return """
GitHub MCP Server
-----------------
A comprehensive GitHub integration service that enables:
- Repository management (create, list, fork, get details)
- Issue tracking (create, update, list, search, comment)
- Pull request operations (create, merge, list, get details)
- File operations (read, write, push single/multiple files)
- Search capabilities (repos, code, issues, users)
- Branch management (create, list commits)

Available tools:
- 'github_authenticate': Set GitHub personal access token
- 'github_list_repos': List repositories for user/org
- 'github_get_repo': Get repository details
- 'github_create_repo': Create new repository
- 'github_list_issues': List issues with filters
- 'github_create_issue': Create new issue
- 'github_get_issue': Get issue details
- 'github_update_issue': Update existing issue
- 'github_add_issue_comment': Add comment to issue
- 'github_list_prs': List pull requests
- 'github_create_pr': Create new pull request
- 'github_get_pr': Get pull request details
- 'github_merge_pr': Merge pull request
- 'github_get_file': Get file contents
- 'github_push_file': Create/update single file
- 'github_push_files': Push multiple files in one commit
- 'github_search_repos': Search repositories
- 'github_search_code': Search code across repos
- 'github_search_issues': Search issues/PRs
- 'github_search_users': Search users
- 'github_fork_repo': Fork repository
- 'github_create_branch': Create new branch
- 'github_list_commits': List repository commits

Authentication:
Set GITHUB_TOKEN environment variable with your GitHub Personal Access Token.
Required scopes: repo, user, read:org (adjust based on needed operations).

Integration notes:
- Follows GitHub API v4 REST patterns
- Supports pagination for large result sets
- Includes comprehensive error handling and logging
- Rate limiting aware with proper error messages
"""

if __name__ == "__main__":
    logger.info("Starting GitHub MCP server...")
    mcp.run()