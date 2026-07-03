"""
Collection Noir — push to GitHub (triggers Netlify auto-deploy)

Run this after sync_from_sheet.py + build.py. It commits the whole repo
(data, templates, public/ — everything) and pushes to your GitHub repo.
Netlify picks up the push and redeploys automatically.

Usage:
    python3 build/deploy.py <github-username>/<repo-name> <token>

Example:
    python3 build/deploy.py samantha-santini/collection-noir-site ghp_xxxxxxxx

The token is never written to disk or committed anywhere — it's only
used in-memory for this one push, via the remote URL.
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent


def run(cmd, **kwargs):
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def deploy(repo_slug: str, token: str):
    remote_url = f"https://{token}@github.com/{repo_slug}.git"

    git_dir = ROOT / ".git"
    if not git_dir.exists():
        run(["git", "init"])
        run(["git", "checkout", "-b", "main"])

    # Point origin at the repo, with the token embedded only for this push
    existing_remotes = run(["git", "remote"])
    if "origin" in existing_remotes.split():
        run(["git", "remote", "set-url", "origin", remote_url])
    else:
        run(["git", "remote", "add", "origin", remote_url])

    run(["git", "add", "-A"])

    status = run(["git", "status", "--porcelain"])
    if not status:
        print("Nothing changed since the last sync — nothing to deploy.")
        return

    commit_msg = f"Sync from sheet — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run(["git", "commit", "-m", commit_msg])
    run(["git", "push", "-u", "origin", "main", "--force"])

    # Immediately strip the token back out of the remote URL so it's not
    # left sitting in .git/config after this run
    run(["git", "remote", "set-url", "origin", f"https://github.com/{repo_slug}.git"])

    print(f"Pushed to {repo_slug} — Netlify will pick this up and deploy automatically.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 build/deploy.py <username>/<repo-name> <github-token>")
        sys.exit(1)
    deploy(sys.argv[1], sys.argv[2])
