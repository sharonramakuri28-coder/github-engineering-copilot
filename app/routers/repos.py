from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

from app.auth import decode_token
from app.ai_client import analyze_pr_with_ai, analyze_issue_with_ai

load_dotenv()

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-engineering-copilot"
}

def check_user(authorization: str | None):
    if not authorization:
        return "demo-user"

    token = authorization.replace("Bearer ", "")
    return decode_token(token)

class IssueRequest(BaseModel):
    title: str
    body: str = ""

@router.get("/{owner}/{repo}")
def get_repo(owner: str, repo: str, authorization: str = Header(None)):
    check_user(authorization)

    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Repository not found")

    data = response.json()

    return {
        "name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "language": data["language"],
        "open_issues": data["open_issues_count"],
        "last_updated": data["updated_at"]
    }

@router.get("/{owner}/{repo}/pulls")
def get_pull_requests(owner: str, repo: str, authorization: str = Header(None)):
    check_user(authorization)

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=5"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Pull requests not found")

    prs = response.json()

    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "author": pr["user"]["login"],
            "created_at": pr["created_at"]
        }
        for pr in prs
    ]

@router.get("/{owner}/{repo}/pulls/{pr_number}/summary")
def analyze_pull_request(owner: str, repo: str, pr_number: int, authorization: str = Header(None)):
    check_user(authorization)

    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    diff_headers = {
        **HEADERS,
        "Accept": "application/vnd.github.v3.diff"
    }

    pr_response = requests.get(pr_url, headers=HEADERS)

    if pr_response.status_code != 200:
        raise HTTPException(status_code=404, detail="Pull request not found")

    diff_response = requests.get(pr_url, headers=diff_headers)

    pr = pr_response.json()
    diff_text = diff_response.text if diff_response.status_code == 200 else ""

    analysis = analyze_pr_with_ai(
        pr["title"],
        pr.get("body") or "",
        diff_text
    )

    return {
        "repository": f"{owner}/{repo}",
        "pr_number": pr_number,
        "title": pr["title"],
        "author": pr["user"]["login"],
        "analysis": analysis
    }

@router.post("/{owner}/{repo}/issues/analyze")
def analyze_issue(owner: str, repo: str, request: IssueRequest, authorization: str = Header(None)):
    check_user(authorization)

    analysis = analyze_issue_with_ai(
        request.title,
        request.body
    )

    return {
        "repository": f"{owner}/{repo}",
        "issue_title": request.title,
        "analysis": analysis
    }