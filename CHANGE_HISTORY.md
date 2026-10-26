# CHANGE_HISTORY.md

Newest first. One dated entry per notable change.

## [2026-10-26] — security: PHP2Shell fix for 8.0 and 8.1 via Sury packages
- PHP2Shell (CVE-2026-109618, CVE-2026-109619, critical RCE, exploited in the wild) is fixed upstream in 8.2.35, 8.4.27 and 8.5.12. The official `php` images for those versions carry the fix, so 8.2/8.4/8.5 are unchanged and get it on rebuild.
- 8.0 and 8.1 (EOL; the official images are frozen at 8.0.30/8.1.34) now build `FROM debian:trixie` with PHP from `packages.sury.org/php`. Sury's 2026-10-21 builds (`8.0.30-25`, `8.1.34-9`) backport both CVEs, as their Debian changelog shows.
- These images mimic the official layout (php-fpm on :9000, entrypoint, `/var/www/html`, no php.ini). PHP follows the OS `TZ`, so PHP's timezone changes from UTC to Asia/Jakarta on 8.0/8.1 (maintainer's choice). They drop the build toolchain, `-dev` libraries and `docker-php-ext-*` helpers. They add a few extensions that Debian builds in (calendar, ffi, ftp, gettext, shmop, sysv*, xsl). 8.0 moves off EOL bullseye, which also removes the `archive.debian.org` workaround.

## [2026-10-22] — ci: native arm64 runners
- `build` now runs per version × platform: amd64 on `ubuntu-latest`, arm64 on `ubuntu-24.04-arm` (no QEMU; the emulated arm64 build took ~1 hour). Each pushes by digest.
- New `merge` job per version joins both digests into multi-arch `latest` (fails without both). `merge` and `description` run with `if: !cancelled()` so failing 8.0/8.1 no longer block 8.5's tag or the overview sync.
- Incident the same day: a manual amd64-only `docker push` overwrote the CI multi-arch `php8.5-fpm:latest`; restored with `docker buildx imagetools create`. Rule added to AGENTS.md.

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
