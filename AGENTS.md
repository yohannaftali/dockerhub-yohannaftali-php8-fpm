# AGENTS.md

> **READ THIS FIRST.** Every AI agent working in this repository (Claude, Gemini, Copilot,
> Cursor, ...) must read this file before doing anything else. It is the single source of
> truth for what this project is and how to work on it. After any structural change
> (new file, new workflow, new tag, changed secret), update this file in the same change.
>
> **Compaction rule:** keep this file describing the *current* state. Put dated history in
> [`CHANGE_HISTORY.md`](CHANGE_HISTORY.md).

## Repository

- remote: https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm
- platform: GitHub (use the `gh` CLI; it is already authenticated on the maintainer's machine)
- default branch: `main`
- Docker Hub images (one repository per PHP version): `yohannaftali/php8.0-fpm`,
  `yohannaftali/php8.1-fpm`, `yohannaftali/php8.2-fpm`,
  `yohannaftali/php8.4-fpm`, `yohannaftali/php8.5-fpm` (no 8.3)

## Big Picture

A tiny repo that builds and publishes [PHP-FPM](https://hub.docker.com/_/php) 8.x images with
common extensions, redis/imagick/igbinary, sendmail and Composer. There is no application
code: the product is the Docker Hub images and their listings.

```
8.X/Dockerfile ──► GitHub Actions (matrix 8.0/8.1/8.2/8.4/8.5, amd64+arm64) ──► Docker Hub yohannaftali/php8.X-fpm
README.md  ──► peter-evans/dockerhub-description / scripts/dockerhub-update.sh ──► each Hub overview
```

Origin: `php8.0-fpm`, `php8.1-fpm` and `php8.2-fpm` were originally pushed in 2023 without a source
repository. The Dockerfile here was reconstructed from `docker history` of those images
(2026-10-05). Since 2026-10-22 each PHP version has its own `<version>/Dockerfile`.

## Repository Layout

```
<version>/Dockerfile             # 8.0, 8.1, 8.2, 8.4, 8.5: FROM php:8.X-fpm; extensions, pecl, sendmail, composer
README.md                        # human docs AND the Docker Hub overview (synced as-is to all repos)
AGENTS.md / CHANGE_HISTORY.md    # agent guide / dated history
CLAUDE.md                        # points agents at this file
.env.example                     # variable names only; real .env is git-ignored
.github/workflows/docker-publish.yml   # build+push matrix, then description sync
scripts/dockerhub_update.py      # Docker Hub API helper for all repos (stdlib only, run via uv)
scripts/dockerhub-update.sh|.ps1 # bash / PowerShell wrappers around `uv run`
.claude/skills/                  # planner, coder, tester, reviewer (see below)
```

## Key Facts

- **Versions** are the `php` matrix in both jobs of `docker-publish.yml` and `VERSIONS` in
  `scripts/dockerhub_update.py`. Adding or dropping a version means editing all three, adding or removing
  `<version>/Dockerfile`, **and** the table in `README.md`. Each version publishes a single tag, `latest`, to its own Hub repository.
- The workflow runs on push to `main`, weekly (Mon 03:00 UTC) and manually. The `description` job
  syncs `README.md` and the per-version short description after the builds pass.
- **Secrets** (GitHub repo secrets): `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` (Docker Hub PAT,
  scope *Read, Write, Delete*; description updates need Delete scope).
- **Categories cannot be set via the Docker Hub API** (it silently ignores them). They are set
  by hand in the web UI for each repository. Not set yet.
- `README.md` is published verbatim as every Hub overview: keep it self-contained, no
  repo-relative links that only work on GitHub.
- Related repos: `dockerhub-yohannaftali-php7-fpm` (PHP 7.4) and `dockerhub-yohannaftali-php7.0.33-fpm`
  (PHP 7.0.33). Legacy duplicate Hub repos for other images are frozen, see those repos' notes.

## Conventions & Guardrails

- Never commit `.env` or any token. `.env.example` holds names and placeholders only.
- Never print tokens in output, logs or commit messages. Refer to them as `$TOKEN`.
- One Dockerfile per PHP version in `<version>/Dockerfile` (decided 2026-10-22). Keep them close to
  the official image and to each other: a shared change (package, extension, entrypoint) goes into
  every file. Version-specific differences stay in that version's file only.
- PHP 8.0 is built on Debian 11 (bullseye, EOL): `8.0/Dockerfile` points apt at `archive.debian.org`.
- OPcache is compiled into PHP 8.5, so `8.5/Dockerfile` does not `docker-php-ext-install` it.
- xdebug is deliberately **not** installed (production images, removed 2026-10-22).
- PHP `date.timezone` is deliberately **not** set (stays UTC, decided 2026-10-05: keep PHP
  datetime-agnostic). `TZ=Asia/Jakarta` only affects the OS clock. Do not add `date.timezone`
  without asking.
- These images are in use by other apps under their existing names. Never rename or delete the Hub
  repositories, and never push anything except `latest` builds of the same PHP minor version.
- Python scripts are stdlib-only and run through `uv`; bash and PowerShell wrappers stay thin and
  behave identically.
- Commit message ends with the attribution trailer configured for the session.
- Pushing to `main` publishes images to Docker Hub. Treat it as a release.

## Validation (before pushing)

```bash
docker build -f 8.2/Dockerfile -t php-test .
docker run --rm php-test php -v                       # PHP 8.2.x
docker run --rm php-test date +%Z                     # WIB (OS)
docker run --rm php-test php -r 'echo date_default_timezone_get();'   # UTC (by design)
docker run --rm php-test composer --version
docker run --rm php-test php-fpm -t                   # config valid
uv run scripts/dockerhub_update.py status             # needs .env; read-only
```

Repeat the build for every version in the matrix (at least 8.0, which uses the older Debian base).
See the `tester` skill for the full smoke test.

## Agent Skills (`.claude/skills/`)

Adapted from the sibling Docker Hub repos (no issue-tracker UI, no browser).

- **`planner`**: create/track GitHub issues with `gh`; keeps the Tracked Issues table current.
- **`coder`**: implements an issue (Dockerfile, workflow, scripts, README) per these rules.
- **`tester`**: builds each version locally, smoke-tests it, and only then opens/merges a PR.
- **`reviewer`**: post-merge audit of what landed on `main` and on Docker Hub.

Flow: `planner` -> `coder` -> `tester` -> `reviewer`.

## Tracked Issues

| ID | Title | Status | Last Checked |
|----|-------|--------|--------------|

## Change Log Policy

- `AGENTS.md`: current architecture and rules only.
- `CHANGE_HISTORY.md`: one dated entry per notable change, newest first.
- Any agent making a structural change updates both files in the same change.
