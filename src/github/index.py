"""
GitHub integration core functionality
"""

import os
import json
import logging
import requests
import base64
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

# Global variable to store authenticated session
github_session = None
authenticated_user = None

def get_github_token():
    """Get GitHub token from environment variable"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return token

def get_authenticated_session():
    """Get or create authenticated session"""
    global github_session, authenticated_user
    
    if github_session is None:
        token = get_github_token()
        github_session = requests.Session()
        github_session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-MCP-Server/1.0'
        })
        
        # Verify authentication
        response = github_session.get(f"{GITHUB_API_BASE}/user")
        if response.status_code != 200:
            raise Exception(f"GitHub authentication failed: {response.status_code}")
        
        authenticated_user = response.json()
        logger.info(f"Authenticated as: {authenticated_user.get('login')}")
    
    return github_session

def authenticate_github(token: str) -> Dict:
    """
    Authenticate with GitHub using personal access token
    
    Args:
        token: GitHub personal access token
    
    Returns:
        Authentication status and user information
    """
    global github_session, authenticated_user
    
    # Set token in environment for session creation
    os.environ['GITHUB_TOKEN'] = token
    
    # Reset session to force re-authentication
    github_session = None
    authenticated_user = None
    
    try:
        session = get_authenticated_session()
        return {
            "success": True,
            "user": authenticated_user,
            "message": f"Successfully authenticated as {authenticated_user.get('login')}"
        }
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Authentication failed. Please check your token."
        }

def list_repositories(owner: str = None, type: str = "all", sort: str = "updated", per_page: int = 30) -> Dict:
    """List GitHub repositories"""
    session = get_authenticated_session()
    
    if owner:
        # List repositories for specific user/org
        url = f"{GITHUB_API_BASE}/users/{owner}/repos"
    else:
        # List repositories for authenticated user
        url = f"{GITHUB_API_BASE}/user/repos"
    
    params = {
        "type": type,
        "sort": sort,
        "per_page": min(per_page, 100)
    }
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    repos = response.json()
    
    return {
        "success": True,
        "repositories": [
            {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "private": repo["private"],
                "html_url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "ssh_url": repo["ssh_url"],
                "default_branch": repo["default_branch"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "open_issues": repo["open_issues_count"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "pushed_at": repo["pushed_at"]
            }
            for repo in repos
        ],
        "count": len(repos)
    }

def get_repository(owner: str, repo: str) -> Dict:
    """Get detailed repository information"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    response = session.get(url)
    response.raise_for_status()
    
    repo_data = response.json()
    
    return {
        "success": True,
        "repository": {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data["description"],
            "private": repo_data["private"],
            "html_url": repo_data["html_url"],
            "clone_url": repo_data["clone_url"],
            "ssh_url": repo_data["ssh_url"],
            "default_branch": repo_data["default_branch"],
            "language": repo_data["language"],
            "languages_url": repo_data["languages_url"],
            "topics": repo_data.get("topics", []),
            "stars": repo_data["stargazers_count"],
            "watchers": repo_data["watchers_count"],
            "forks": repo_data["forks_count"],
            "open_issues": repo_data["open_issues_count"],
            "size": repo_data["size"],
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"],
            "pushed_at": repo_data["pushed_at"],
            "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            "owner": {
                "login": repo_data["owner"]["login"],
                "id": repo_data["owner"]["id"],
                "type": repo_data["owner"]["type"]
            }
        }
    }

def create_repository(name: str, description: str = None, private: bool = False, auto_init: bool = True) -> Dict:
    """Create a new repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/user/repos"
    
    data = {
        "name": name,
        "private": private,
        "auto_init": auto_init
    }
    
    if description:
        data["description"] = description
    
    response = session.post(url, json=data)
    response.raise_for_status()
    
    repo_data = response.json()
    
    return {
        "success": True,
        "repository": {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data["description"],
            "private": repo_data["private"],
            "html_url": repo_data["html_url"],
            "clone_url": repo_data["clone_url"],
            "ssh_url": repo_data["ssh_url"],
            "default_branch": repo_data["default_branch"]
        },
        "message": f"Repository {name} created successfully"
    }

def list_issues(owner: str, repo: str, state: str = "open", labels: str = None, assignee: str = None, per_page: int = 30) -> Dict:
    """List issues in a repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    
    params = {
        "state": state,
        "per_page": min(per_page, 100)
    }
    
    if labels:
        params["labels"] = labels
    if assignee:
        params["assignee"] = assignee
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    issues = response.json()
    
    return {
        "success": True,
        "issues": [
            {
                "id": issue["id"],
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "state": issue["state"],
                "html_url": issue["html_url"],
                "user": {
                    "login": issue["user"]["login"],
                    "id": issue["user"]["id"]
                },
                "assignees": [{"login": a["login"], "id": a["id"]} for a in issue["assignees"]],
                "labels": [{"name": l["name"], "color": l["color"]} for l in issue["labels"]],
                "comments": issue["comments"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "closed_at": issue["closed_at"]
            }
            for issue in issues if not issue.get("pull_request")  # Filter out PRs
        ],
        "count": len([i for i in issues if not i.get("pull_request")])
    }

def create_issue(owner: str, repo: str, title: str, body: str = None, assignees: List[str] = None, labels: List[str] = None) -> Dict:
    """Create a new issue"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    
    data = {"title": title}
    
    if body:
        data["body"] = body
    if assignees:
        data["assignees"] = assignees
    if labels:
        data["labels"] = labels
    
    response = session.post(url, json=data)
    response.raise_for_status()
    
    issue = response.json()
    
    return {
        "success": True,
        "issue": {
            "id": issue["id"],
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "html_url": issue["html_url"],
            "user": {
                "login": issue["user"]["login"],
                "id": issue["user"]["id"]
            },
            "assignees": [{"login": a["login"], "id": a["id"]} for a in issue["assignees"]],
            "labels": [{"name": l["name"], "color": l["color"]} for l in issue["labels"]],
            "created_at": issue["created_at"]
        },
        "message": f"Issue #{issue['number']} created successfully"
    }

def get_issue(owner: str, repo: str, issue_number: int) -> Dict:
    """Get details of a specific issue"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
    response = session.get(url)
    response.raise_for_status()
    
    issue = response.json()
    
    # Get comments
    comments_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    comments_response = session.get(comments_url)
    comments = comments_response.json() if comments_response.status_code == 200 else []
    
    return {
        "success": True,
        "issue": {
            "id": issue["id"],
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "html_url": issue["html_url"],
            "user": {
                "login": issue["user"]["login"],
                "id": issue["user"]["id"]
            },
            "assignees": [{"login": a["login"], "id": a["id"]} for a in issue["assignees"]],
            "labels": [{"name": l["name"], "color": l["color"]} for l in issue["labels"]],
            "comments_count": issue["comments"],
            "comments": [
                {
                    "id": comment["id"],
                    "body": comment["body"],
                    "user": {"login": comment["user"]["login"], "id": comment["user"]["id"]},
                    "created_at": comment["created_at"],
                    "updated_at": comment["updated_at"]
                }
                for comment in comments
            ],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
            "closed_at": issue["closed_at"]
        }
    }

def update_issue(owner: str, repo: str, issue_number: int, title: str = None, body: str = None, state: str = None, assignees: List[str] = None, labels: List[str] = None) -> Dict:
    """Update an existing issue"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
    
    data = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if state is not None:
        data["state"] = state
    if assignees is not None:
        data["assignees"] = assignees
    if labels is not None:
        data["labels"] = labels
    
    response = session.patch(url, json=data)
    response.raise_for_status()
    
    issue = response.json()
    
    return {
        "success": True,
        "issue": {
            "id": issue["id"],
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "html_url": issue["html_url"],
            "updated_at": issue["updated_at"]
        },
        "message": f"Issue #{issue['number']} updated successfully"
    }

def add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> Dict:
    """Add a comment to an issue"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    data = {"body": body}
    
    response = session.post(url, json=data)
    response.raise_for_status()
    
    comment = response.json()
    
    return {
        "success": True,
        "comment": {
            "id": comment["id"],
            "body": comment["body"],
            "user": {
                "login": comment["user"]["login"],
                "id": comment["user"]["id"]
            },
            "html_url": comment["html_url"],
            "created_at": comment["created_at"]
        },
        "message": f"Comment added to issue #{issue_number}"
    }

def list_pull_requests(owner: str, repo: str, state: str = "open", head: str = None, base: str = None, per_page: int = 30) -> Dict:
    """List pull requests in a repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    
    params = {
        "state": state,
        "per_page": min(per_page, 100)
    }
    
    if head:
        params["head"] = head
    if base:
        params["base"] = base
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    prs = response.json()
    
    return {
        "success": True,
        "pull_requests": [
            {
                "id": pr["id"],
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"],
                "state": pr["state"],
                "draft": pr["draft"],
                "html_url": pr["html_url"],
                "user": {
                    "login": pr["user"]["login"],
                    "id": pr["user"]["id"]
                },
                "head": {
                    "ref": pr["head"]["ref"],
                    "sha": pr["head"]["sha"],
                    "repo": pr["head"]["repo"]["full_name"] if pr["head"]["repo"] else None
                },
                "base": {
                    "ref": pr["base"]["ref"],
                    "sha": pr["base"]["sha"],
                    "repo": pr["base"]["repo"]["full_name"]
                },
                "mergeable": pr["mergeable"],
                "merged": pr["merged"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "closed_at": pr["closed_at"],
                "merged_at": pr["merged_at"]
            }
            for pr in prs
        ],
        "count": len(prs)
    }

def create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = None, draft: bool = False) -> Dict:
    """Create a new pull request"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    
    data = {
        "title": title,
        "head": head,
        "base": base,
        "draft": draft
    }
    
    if body:
        data["body"] = body
    
    response = session.post(url, json=data)
    response.raise_for_status()
    
    pr = response.json()
    
    return {
        "success": True,
        "pull_request": {
            "id": pr["id"],
            "number": pr["number"],
            "title": pr["title"],
            "body": pr["body"],
            "state": pr["state"],
            "draft": pr["draft"],
            "html_url": pr["html_url"],
            "head": {
                "ref": pr["head"]["ref"],
                "sha": pr["head"]["sha"]
            },
            "base": {
                "ref": pr["base"]["ref"],
                "sha": pr["base"]["sha"]
            },
            "created_at": pr["created_at"]
        },
        "message": f"Pull request #{pr['number']} created successfully"
    }

def get_pull_request(owner: str, repo: str, pull_number: int) -> Dict:
    """Get details of a specific pull request"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pull_number}"
    response = session.get(url)
    response.raise_for_status()
    
    pr = response.json()
    
    # Get files changed
    files_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pull_number}/files"
    files_response = session.get(files_url)
    files = files_response.json() if files_response.status_code == 200 else []
    
    return {
        "success": True,
        "pull_request": {
            "id": pr["id"],
            "number": pr["number"],
            "title": pr["title"],
            "body": pr["body"],
            "state": pr["state"],
            "draft": pr["draft"],
            "html_url": pr["html_url"],
            "user": {
                "login": pr["user"]["login"],
                "id": pr["user"]["id"]
            },
            "head": {
                "ref": pr["head"]["ref"],
                "sha": pr["head"]["sha"],
                "repo": pr["head"]["repo"]["full_name"] if pr["head"]["repo"] else None
            },
            "base": {
                "ref": pr["base"]["ref"],
                "sha": pr["base"]["sha"],
                "repo": pr["base"]["repo"]["full_name"]
            },
            "mergeable": pr["mergeable"],
            "mergeable_state": pr["mergeable_state"],
            "merged": pr["merged"],
            "commits": pr["commits"],
            "additions": pr["additions"],
            "deletions": pr["deletions"],
            "changed_files": pr["changed_files"],
            "files": [
                {
                    "filename": f["filename"],
                    "status": f["status"],
                    "additions": f["additions"],
                    "deletions": f["deletions"],
                    "changes": f["changes"],
                    "patch": f.get("patch", "")[:1000]  # Truncate large patches
                }
                for f in files
            ],
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "closed_at": pr["closed_at"],
            "merged_at": pr["merged_at"]
        }
    }

def merge_pull_request(owner: str, repo: str, pull_number: int, commit_title: str = None, commit_message: str = None, merge_method: str = "merge") -> Dict:
    """Merge a pull request"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pull_number}/merge"
    
    data = {"merge_method": merge_method}
    
    if commit_title:
        data["commit_title"] = commit_title
    if commit_message:
        data["commit_message"] = commit_message
    
    response = session.put(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    return {
        "success": True,
        "merge": {
            "sha": result["sha"],
            "merged": result["merged"],
            "message": result["message"]
        },
        "message": f"Pull request #{pull_number} merged successfully"
    }

def get_file_contents(owner: str, repo: str, path: str, branch: str = None) -> Dict:
    """Get contents of a file from repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    
    params = {}
    if branch:
        params["ref"] = branch
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    content = response.json()
    
    # Decode content if it's base64 encoded
    decoded_content = None
    if content.get("encoding") == "base64":
        try:
            decoded_content = base64.b64decode(content["content"]).decode('utf-8')
        except UnicodeDecodeError:
            decoded_content = "[Binary file - cannot display as text]"
    
    return {
        "success": True,
        "file": {
            "name": content["name"],
            "path": content["path"],
            "sha": content["sha"],
            "size": content["size"],
            "type": content["type"],
            "encoding": content.get("encoding"),
            "content": decoded_content,
            "content_base64": content["content"] if content.get("encoding") == "base64" else None,
            "html_url": content["html_url"],
            "download_url": content["download_url"]
        }
    }

def create_or_update_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = None, sha: str = None) -> Dict:
    """Create or update a file in repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    
    # Encode content as base64
    content_encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    
    data = {
        "message": message,
        "content": content_encoded
    }
    
    if branch:
        data["branch"] = branch
    if sha:  # Required for updates
        data["sha"] = sha
    
    response = session.put(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    return {
        "success": True,
        "commit": {
            "sha": result["commit"]["sha"],
            "html_url": result["commit"]["html_url"],
            "message": result["commit"]["message"],
            "author": result["commit"]["author"]
        },
        "content": {
            "name": result["content"]["name"],
            "path": result["content"]["path"],
            "sha": result["content"]["sha"],
            "html_url": result["content"]["html_url"]
        },
        "message": f"File {path} {'updated' if sha else 'created'} successfully"
    }

def push_files(owner: str, repo: str, files: List[Dict], message: str, branch: str = None) -> Dict:
    """Push multiple files to repository in single commit"""
    session = get_authenticated_session()
    
    # This is a simplified implementation that pushes files one by one
    # For a true atomic multi-file commit, you'd need to use the Git Trees API
    results = []
    
    for file_info in files:
        try:
            result = create_or_update_file(
                owner, repo, 
                file_info["path"], 
                file_info["content"], 
                message, 
                branch, 
                file_info.get("sha")
            )
            results.append({
                "path": file_info["path"],
                "success": True,
                "sha": result["commit"]["sha"]
            })
        except Exception as e:
            results.append({
                "path": file_info["path"],
                "success": False,
                "error": str(e)
            })
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    return {
        "success": len(failed) == 0,
        "results": results,
        "summary": {
            "total": len(files),
            "successful": len(successful),
            "failed": len(failed)
        },
        "message": f"Pushed {len(successful)}/{len(files)} files successfully"
    }

def search_repositories(query: str, sort: str = "stars", order: str = "desc", per_page: int = 30) -> Dict:
    """Search GitHub repositories"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/search/repositories"
    
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100)
    }
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    results = response.json()
    
    return {
        "success": True,
        "total_count": results["total_count"],
        "incomplete_results": results["incomplete_results"],
        "repositories": [
            {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "private": repo["private"],
                "html_url": repo["html_url"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "open_issues": repo["open_issues_count"],
                "topics": repo.get("topics", []),
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "owner": {
                    "login": repo["owner"]["login"],
                    "type": repo["owner"]["type"]
                }
            }
            for repo in results["items"]
        ]
    }

def search_code(query: str, sort: str = None, order: str = "desc", per_page: int = 30) -> Dict:
    """Search code across GitHub repositories"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/search/code"
    
    params = {
        "q": query,
        "order": order,
        "per_page": min(per_page, 100)
    }
    
    if sort:
        params["sort"] = sort
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    results = response.json()
    
    return {
        "success": True,
        "total_count": results["total_count"],
        "incomplete_results": results["incomplete_results"],
        "code_results": [
            {
                "name": item["name"],
                "path": item["path"],
                "sha": item["sha"],
                "html_url": item["html_url"],
                "repository": {
                    "id": item["repository"]["id"],
                    "name": item["repository"]["name"],
                    "full_name": item["repository"]["full_name"],
                    "html_url": item["repository"]["html_url"],
                    "owner": {
                        "login": item["repository"]["owner"]["login"],
                        "type": item["repository"]["owner"]["type"]
                    }
                }
            }
            for item in results["items"]
        ]
    }

def search_issues(query: str, sort: str = "created", order: str = "desc", per_page: int = 30) -> Dict:
    """Search issues and pull requests across GitHub"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/search/issues"
    
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100)
    }
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    results = response.json()
    
    return {
        "success": True,
        "total_count": results["total_count"],
        "incomplete_results": results["incomplete_results"],
        "issues": [
            {
                "id": item["id"],
                "number": item["number"],
                "title": item["title"],
                "body": item["body"][:500] if item["body"] else None,  # Truncate long bodies
                "state": item["state"],
                "html_url": item["html_url"],
                "user": {
                    "login": item["user"]["login"],
                    "id": item["user"]["id"]
                },
                "labels": [{"name": l["name"], "color": l["color"]} for l in item["labels"]],
                "assignees": [{"login": a["login"], "id": a["id"]} for a in item.get("assignees", [])],
                "comments": item["comments"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "closed_at": item["closed_at"],
                "repository": {
                    "id": item["repository_url"].split("/")[-1],
                    "full_name": "/".join(item["repository_url"].split("/")[-2:])
                },
                "is_pull_request": "pull_request" in item
            }
            for item in results["items"]
        ]
    }

def search_users(query: str, sort: str = "joined", order: str = "desc", per_page: int = 30) -> Dict:
    """Search GitHub users"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/search/users"
    
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100)
    }
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    results = response.json()
    
    return {
        "success": True,
        "total_count": results["total_count"],
        "incomplete_results": results["incomplete_results"],
        "users": [
            {
                "id": user["id"],
                "login": user["login"],
                "type": user["type"],
                "html_url": user["html_url"],
                "avatar_url": user["avatar_url"],
                "score": user["score"]
            }
            for user in results["items"]
        ]
    }

def fork_repository(owner: str, repo: str, organization: str = None) -> Dict:
    """Fork a repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/forks"
    
    data = {}
    if organization:
        data["organization"] = organization
    
    response = session.post(url, json=data if data else None)
    response.raise_for_status()
    
    fork = response.json()
    
    return {
        "success": True,
        "fork": {
            "id": fork["id"],
            "name": fork["name"],
            "full_name": fork["full_name"],
            "html_url": fork["html_url"],
            "clone_url": fork["clone_url"],
            "ssh_url": fork["ssh_url"],
            "owner": {
                "login": fork["owner"]["login"],
                "id": fork["owner"]["id"]
            },
            "parent": {
                "full_name": fork["parent"]["full_name"],
                "html_url": fork["parent"]["html_url"]
            }
        },
        "message": f"Repository {owner}/{repo} forked successfully"
    }

def create_branch(owner: str, repo: str, branch: str, from_branch: str = None) -> Dict:
    """Create a new branch"""
    session = get_authenticated_session()
    
    # First, get the SHA of the source branch (or default branch)
    if from_branch:
        ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{from_branch}"
    else:
        # Get default branch
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        repo_response = session.get(repo_url)
        repo_response.raise_for_status()
        default_branch = repo_response.json()["default_branch"]
        ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{default_branch}"
    
    ref_response = session.get(ref_url)
    ref_response.raise_for_status()
    
    source_sha = ref_response.json()["object"]["sha"]
    
    # Create new branch reference
    create_ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs"
    
    data = {
        "ref": f"refs/heads/{branch}",
        "sha": source_sha
    }
    
    response = session.post(create_ref_url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    return {
        "success": True,
        "branch": {
            "name": branch,
            "ref": result["ref"],
            "sha": result["object"]["sha"],
            "url": result["url"]
        },
        "message": f"Branch {branch} created successfully"
    }

def list_commits(owner: str, repo: str, sha: str = None, path: str = None, per_page: int = 30) -> Dict:
    """List commits in a repository"""
    session = get_authenticated_session()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    
    params = {"per_page": min(per_page, 100)}
    
    if sha:
        params["sha"] = sha
    if path:
        params["path"] = path
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    commits = response.json()
    
    return {
        "success": True,
        "commits": [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": {
                    "name": commit["commit"]["author"]["name"],
                    "email": commit["commit"]["author"]["email"],
                    "date": commit["commit"]["author"]["date"]
                },
                "committer": {
                    "name": commit["commit"]["committer"]["name"],
                    "email": commit["commit"]["committer"]["email"],
                    "date": commit["commit"]["committer"]["date"]
                },
                "html_url": commit["html_url"],
                "stats": commit.get("stats", {}),
                "files": len(commit.get("files", [])) if commit.get("files") else None
            }
            for commit in commits
        ],
        "count": len(commits)
    }