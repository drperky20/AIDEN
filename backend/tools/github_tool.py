from github import Github

class GitHubTool:
    """
    Tool for interacting with the GitHub API for automation.
    Usage: run(token: str, repo: str, action: str, params: dict) -> dict
    Supported actions: 'create_issue', 'close_issue', 'list_issues'
    """
    def run(self, token: str, repo: str, action: str, params: dict) -> dict:
        try:
            g = Github(token)
            repository = g.get_repo(repo)
            if action == 'create_issue':
                issue = repository.create_issue(title=params['title'], body=params.get('body', ''))
                return {"status": "success", "issue_number": issue.number}
            elif action == 'close_issue':
                issue = repository.get_issue(number=params['issue_number'])
                issue.edit(state='closed')
                return {"status": "success", "closed": True}
            elif action == 'list_issues':
                issues = repository.get_issues(state=params.get('state', 'open'))
                return {"status": "success", "issues": [i.title for i in issues]}
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}