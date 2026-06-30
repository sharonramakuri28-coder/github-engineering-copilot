import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

CLAUDE_HEADERS = {
    "x-api-key": CLAUDE_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

def call_claude(prompt: str):
    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "your_claude_api_key_here":
        return None

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=CLAUDE_HEADERS,
        json={
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 600,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        },
        timeout=30
    )

    if response.status_code != 200:
        return None

    return response.json()["content"][0]["text"]


def analyze_pr_with_ai(pr_title: str, pr_body: str, diff_text: str):
    prompt = f"""
Analyze this GitHub pull request.

Return ONLY valid JSON in this format:
{{
  "summary": "short plain English summary",
  "risk_level": "low / medium / high",
  "risk_reason": "why this risk level was chosen",
  "breaking_change_flag": true,
  "reviewer_note": "what reviewer should check"
}}

PR Title:
{pr_title}

PR Description:
{pr_body}

Code Diff:
{diff_text[:3000]}
"""

    result = call_claude(prompt)

    if result:
        try:
            return json.loads(result)
        except Exception:
            return {
                "summary": result,
                "risk_level": "unknown",
                "risk_reason": "Claude returned text instead of JSON",
                "breaking_change_flag": False,
                "reviewer_note": "Review manually"
            }

    return {
        "summary": f"This pull request appears to update code related to: {pr_title}.",
        "risk_level": "medium" if len(diff_text) > 1500 else "low",
        "risk_reason": "Fallback analysis based on diff size because Claude API was unavailable.",
        "breaking_change_flag": "breaking" in diff_text.lower(),
        "reviewer_note": "Review changed files, logic updates, and possible side effects."
    }


def analyze_issue_with_ai(title: str, body: str):
    prompt = f"""
Analyze this GitHub issue.

Return ONLY valid JSON in this format:
{{
  "category": "bug / feature / documentation / performance / security / general",
  "priority": "low / medium / high / critical",
  "root_cause_hypothesis": "likely reason",
  "recommended_next_step": "what engineering team should do next"
}}

Issue Title:
{title}

Issue Body:
{body}
"""

    result = call_claude(prompt)

    if result:
        try:
            return json.loads(result)
        except Exception:
            return {
                "category": "general",
                "priority": "medium",
                "root_cause_hypothesis": result,
                "recommended_next_step": "Review manually"
            }

    text = f"{title} {body}".lower()

    if "login" in text or "auth" in text or "token" in text:
        category = "authentication"
        priority = "high"
    elif "slow" in text or "timeout" in text:
        category = "performance"
        priority = "high"
    elif "crash" in text or "error" in text:
        category = "bug"
        priority = "high"
    else:
        category = "general"
        priority = "medium"

    return {
        "category": category,
        "priority": priority,
        "root_cause_hypothesis": f"The issue may be related to {category} logic.",
        "recommended_next_step": "Reproduce the issue, check logs, identify affected files, and assign it to the relevant developer."
    }