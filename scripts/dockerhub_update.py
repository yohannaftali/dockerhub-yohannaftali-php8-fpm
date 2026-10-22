#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Update the Docker Hub repositories built from this repo (stdlib only).

This repo publishes one Docker Hub repository per PHP version (php8.0-fpm, php8.1-fpm, php8.2-fpm).

Usage:
  uv run scripts/dockerhub_update.py                     # sync README + short description to ALL repos
  uv run scripts/dockerhub_update.py sync [repo]          # ... or just one (e.g. php8.2-fpm)
  uv run scripts/dockerhub_update.py status [repo]        # description, categories, pulls
  uv run scripts/dockerhub_update.py tags [repo]          # list tags
  uv run scripts/dockerhub_update.py delete-tag <repo> <tag>

Reads DOCKERHUB_USERNAME and DOCKERHUB_TOKEN from the environment or .env.
The token needs "Read, Write, Delete" scope.
Categories cannot be set through the API; use the Docker Hub web UI.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://hub.docker.com/v2"
VERSIONS = ["8.0", "8.1", "8.2", "8.4", "8.5"]
REPOS = [f"php{v}-fpm" for v in VERSIONS]


def short_description(repo):
    version = repo.removeprefix("php").removesuffix("-fpm")
    return f"PHP {version}-FPM with redis, imagick, igbinary, sendmail and Composer. PHP stays UTC."


def load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and not line.lstrip().startswith("#"):
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def request(method, url, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        raw = res.read()
        return json.loads(raw) if raw else None


def pick_repos(name):
    if name is None:
        return REPOS
    if name not in REPOS:
        sys.exit(f"unknown repo {name!r}; expected one of {', '.join(REPOS)}")
    return [name]


def main():
    load_env()
    user = os.environ.get("DOCKERHUB_USERNAME")
    password = os.environ.get("DOCKERHUB_TOKEN")
    if not user or not password:
        sys.exit("DOCKERHUB_USERNAME and DOCKERHUB_TOKEN must be set (env or .env)")

    jwt = request("POST", f"{API}/users/login", {"username": user, "password": password})["token"]
    args = sys.argv[1:]
    cmd = args[0] if args else "sync"
    arg1 = args[1] if len(args) > 1 else None

    def url(repo):
        return f"{API}/repositories/{user}/{repo}"

    def status(repo):
        r = request("GET", url(repo) + "/", token=jwt)
        print(json.dumps({
            "name": f"{user}/{repo}",
            "description": r["description"],
            "categories": [c["name"] for c in r.get("categories") or []],
            "pull_count": r["pull_count"],
            "star_count": r["star_count"],
            "last_updated": r["last_updated"],
        }, indent=2))

    if cmd == "sync":
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for repo in pick_repos(arg1):
            request("PATCH", url(repo) + "/",
                    {"description": short_description(repo), "full_description": readme}, jwt)
            print(f"Updated description and overview for {user}/{repo}")
            status(repo)
    elif cmd == "status":
        for repo in pick_repos(arg1):
            status(repo)
    elif cmd == "tags":
        for repo in pick_repos(arg1):
            print(f"== {repo}")
            for t in request("GET", url(repo) + "/tags?page_size=100", token=jwt)["results"]:
                print(f"{t['name']}\t{t['last_updated']}\t{t['full_size']} bytes")
    elif cmd == "delete-tag" and len(args) == 3:
        repo, tag = pick_repos(args[1])[0], args[2]
        request("DELETE", f"{url(repo)}/tags/{tag}/", token=jwt)
        print(f"Deleted tag {tag} from {repo}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
