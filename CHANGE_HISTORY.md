# CHANGE_HISTORY.md

Newest first. One dated entry per notable change.

## [2026-10-22] — refactor: one Dockerfile per PHP version
- Replaced the parameterised root `Dockerfile` (`PHP_VERSION` build arg) with `8.0/`, `8.1/`, `8.2/`, `8.4/` and `8.5/Dockerfile`, each `FROM php:8.X-fpm`. The workflow builds with `file: <version>/Dockerfile`.
- The bullseye archive fix now lives only in `8.0/Dockerfile`; `8.5/Dockerfile` skips the OPcache install. Image contents unchanged.

## [2026-10-22] — feat: add php8.4-fpm and php8.5-fpm, drop xdebug
- Added PHP 8.4 and 8.5 to the workflow matrix (both jobs), `VERSIONS` in `scripts/dockerhub_update.py` and the README table. The Hub repos `yohannaftali/php8.4-fpm` and `php8.5-fpm` were created by the maintainer beforehand. No 8.3 image.
- Removed xdebug from all images (not used in production; the 3.2.2 pin also did not support PHP 8.4+). Short descriptions and docs updated accordingly.

## [2026-10-05] — feat: source repo for php8.0-fpm, php8.1-fpm and php8.2-fpm
- These three Docker Hub images (pushed 2023-09-05..07, ~290 pulls each, in use by other apps) had no source repository. Reconstructed one parameterised `Dockerfile` from `docker history` of the published images (8.1/8.2 share the same steps; 8.0 had older package names, now unified onto the 8.1/8.2 list).
- Cleanups vs the originals: removed duplicate `pdo_mysql` in `docker-php-ext-install` and duplicate `libzip-dev`; added the bullseye archive fix for PHP 8.0 (its Debian 11 base is EOL).
- `.github/workflows/docker-publish.yml`: matrix `8.0`/`8.1`/`8.2`, amd64+arm64, weekly + on push to `main` + manual, publishing `latest` to each existing Hub repo, then syncs the README and a per-version short description.
- `scripts/dockerhub_update.py` handles all three repos (`sync`, `status`, `tags`, `delete-tag <repo> <tag>`).
- PHP `date.timezone` kept at the default UTC on purpose; only the OS clock uses `TZ=Asia/Jakarta`.
- Added `README.md`, `AGENTS.md`, `CLAUDE.md`, `.env.example`, `.gitignore` and `.claude/skills/` adapted from the sibling repos.
- Docker Hub categories still to be set manually in the web UI.
