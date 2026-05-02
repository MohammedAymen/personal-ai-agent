
import os
import requests
from langchain.schema import Document


GITHUB_API = "https://api.github.com"


def _get_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def _fetch_user_profile(username: str, headers: dict) -> dict:
    resp = requests.get(f"{GITHUB_API}/users/{username}", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _fetch_repos(username: str, headers: dict) -> list[dict]:
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{GITHUB_API}/users/{username}/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "sort": "updated"},
            timeout=10,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def _fetch_languages(repo_full_name: str, headers: dict) -> dict:
    try:
        resp = requests.get(
            f"{GITHUB_API}/repos/{repo_full_name}/languages",
            headers=headers,
            timeout=10,
        )
        return resp.json() if resp.ok else {}
    except Exception:
        return {}


def load_github(username: str, token: str, max_repos: int = 30) -> list[Document]:
    """
    يجيب بيانات GitHub ويرجعها كـ Documents
    """
    if not token or not username:
        print("⚠️  GitHub: مفيش token أو username، هيتخطى")
        return []

    headers = _get_headers(token)
    documents = []

    try:
        
        profile = _fetch_user_profile(username, headers)

        profile_text = f"""
GitHub Profile for {profile.get('name', username)} (@{username})
================================================================
Bio: {profile.get('bio', 'N/A')}
Location: {profile.get('location', 'N/A')}
Company: {profile.get('company', 'N/A')}
Blog/Website: {profile.get('blog', 'N/A')}
Email: {profile.get('email', 'N/A')}
Public Repositories: {profile.get('public_repos', 0)}
Followers: {profile.get('followers', 0)}
Following: {profile.get('following', 0)}
GitHub URL: {profile.get('html_url', '')}
Account Created: {profile.get('created_at', 'N/A')}
""".strip()

        documents.append(
            Document(
                page_content=profile_text,
                metadata={"source": "GitHub", "type": "profile", "username": username},
            )
        )

        
        repos = _fetch_repos(username, headers)
      
        own_repos = [r for r in repos if not r.get("fork", False)]
        top_repos = sorted(own_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:max_repos]

        all_languages = {}
        repos_text_parts = []

        for repo in top_repos:
            langs = _fetch_languages(repo["full_name"], headers)
            for lang, bytes_count in langs.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count

            topics = ", ".join(repo.get("topics", [])) or "None"
            repo_text = (
                f"Repository: {repo['name']}\n"
                f"  Description: {repo.get('description') or 'No description'}\n"
                f"  Language: {repo.get('language') or 'N/A'}\n"
                f"  Stars: {repo.get('stargazers_count', 0)}\n"
                f"  Forks: {repo.get('forks_count', 0)}\n"
                f"  Topics: {topics}\n"
                f"  URL: {repo.get('html_url', '')}\n"
                f"  Last Updated: {repo.get('updated_at', 'N/A')}"
            )
            repos_text_parts.append(repo_text)

        if repos_text_parts:
            repos_summary = f"GitHub Repositories for @{username} ({len(top_repos)} repos shown):\n\n"
            repos_summary += "\n\n".join(repos_text_parts)
            documents.append(
                Document(
                    page_content=repos_summary,
                    metadata={"source": "GitHub", "type": "repositories", "count": len(top_repos)},
                )
            )

        
        if all_languages:
            total = sum(all_languages.values())
            sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)
            langs_text = f"Programming Languages used by @{username} across all repos:\n"
            for lang, bytes_count in sorted_langs[:15]:
                pct = (bytes_count / total * 100) if total else 0
                langs_text += f"  - {lang}: {pct:.1f}%\n"

            documents.append(
                Document(
                    page_content=langs_text,
                    metadata={"source": "GitHub", "type": "languages"},
                )
            )

        print(f"✅ GitHub: اتجلب بروفايل + {len(top_repos)} repo")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ GitHub Token غلط أو منتهي - تأكد من الـ GITHUB_TOKEN في الـ .env")
        elif e.response.status_code == 404:
            print(f"❌ GitHub Username '{username}' مش موجود")
        else:
            print(f"❌ GitHub API Error: {e}")
    except Exception as e:
        print(f"❌ GitHub Error: {e}")

    return documents
