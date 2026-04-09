import datetime
import json
import os
import sys
import urllib.request
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

PRIVATE_TOKEN = os.getenv("privateToken")
USER_NAME = os.getenv("userName")
STORAGE_DIR = "storage"
STARS_FILE = "stars.txt"
GITHUB_API_VERSION = "2022-11-28"
PER_PAGE = 100


def _make_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {PRIVATE_TOKEN}",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }


def get_actual_repos_list():
    repos_list = []
    page_count = 1

    request = urllib.request.Request(
        f"https://api.github.com/user/starred?per_page={PER_PAGE}&page=1",
        headers=_make_headers(),
    )
    with urllib.request.urlopen(request) as f:
        link_header = dict(f.getheaders()).get("Link", "")
        if link_header:
            last_parts = [p for p in link_header.split(",") if 'rel="last"' in p]
            if last_parts:
                tail = last_parts[0]
                page_count = int(tail[tail.rfind("page=") + 5 : tail.rfind(">")])
        first_page = json.loads(f.read().decode("utf-8"))

    repos_list += [
        f"{r['html_url']}\t{r['default_branch']}\t{r['pushed_at']}"
        for r in first_page
    ]

    for page in tqdm(range(2, page_count + 1), initial=1, total=page_count, desc="Fetching pages", unit="page"):
        request = urllib.request.Request(
            f"https://api.github.com/user/starred?per_page={PER_PAGE}&page={page}",
            headers=_make_headers(),
        )
        with urllib.request.urlopen(request) as f:
            data = json.loads(f.read().decode("utf-8"))
        repos_list += [
            f"{r['html_url']}\t{r['default_branch']}\t{r['pushed_at']}"
            for r in data
        ]

    with open(STARS_FILE, "w", encoding="utf-8") as f:
        for item in repos_list:
            f.write(f"{item}\n")

    print(f"Saved {len(repos_list)} starred repos to {STARS_FILE}")


def download_repos(mode="readme"):
    os.makedirs(STORAGE_DIR, exist_ok=True)

    with open(STARS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    skipped = 0
    with tqdm(lines, desc=f"Downloading {mode}", unit="repo") as bar:
        for line in bar:
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue
            repo_url = parts[0]
            repo_branch = parts[1]
            pushed_at = parts[2] if len(parts) > 2 else None
            owner, repo_name = repo_url.strip().split("/")[3:5]
            bar.set_postfix_str(f"{owner}/{repo_name}", refresh=False)

            if mode == "readme":
                was_skipped = _download_readme(owner, repo_name, repo_branch, pushed_at)
                if was_skipped:
                    skipped += 1
            elif mode == "zip":
                was_skipped = _download_zip(owner, repo_name, repo_branch, pushed_at)
                if was_skipped:
                    skipped += 1

    print(f"Done: {len(lines) - skipped} downloaded, {skipped} up to date")


def _download_readme(owner, repo_name, repo_branch, pushed_at=None):
    """Returns True if download was skipped (already up to date)."""
    local_path = f"{STORAGE_DIR}/{owner}_{repo_name}_{repo_branch}.md"

    if pushed_at and os.path.exists(local_path):
        pushed_dt = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        local_mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(local_path), tz=datetime.timezone.utc
        )
        if local_mtime >= pushed_dt:
            return True

    request = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo_name}/readme",
        headers=_make_headers(),
    )
    try:
        with urllib.request.urlopen(request) as f:
            data_url = json.loads(f.read().decode("utf-8"))["download_url"]
        with urllib.request.urlopen(data_url) as f:
            content = f.read().decode("utf-8")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        tqdm.write(f"Error {owner}/{repo_name}: {e}")
    return False


def _download_zip(owner, repo_name, repo_branch, pushed_at=None):
    """Returns True if download was skipped (already up to date)."""
    local_path = f"{STORAGE_DIR}/{owner}_{repo_name}_{repo_branch}.zip"

    if pushed_at and os.path.exists(local_path):
        pushed_dt = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        local_mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(local_path), tz=datetime.timezone.utc
        )
        if local_mtime >= pushed_dt:
            return True

    request = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo_name}/zipball/{repo_branch}",
        headers=_make_headers(),
    )
    try:
        with urllib.request.urlopen(request) as f:
            data = f.read()
        with open(local_path, "wb") as f:
            f.write(data)
    except Exception as e:
        tqdm.write(f"Error {owner}/{repo_name}: {e}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python git_backup.py [update-list | readme | zip]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "update-list":
        get_actual_repos_list()
    elif command in ("readme", "zip"):
        download_repos(mode=command)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
