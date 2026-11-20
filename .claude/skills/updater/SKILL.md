---
name: updater
description: >
  Rebuilds and republishes the php8.X-fpm images on Docker Hub when a newer upstream PHP patch
  release (or Sury package for 8.0/8.1) is available, without changing any code. Compares the
  upstream version with what is published, triggers the CI publish workflow, waits for it and
  verifies the new version and both platforms landed. Use for "update php 8.5", "pull latest",
  "publish 8.5.13 to Docker Hub", "/updater", "/updater 8.4", "are the images up to date?".
---

# Updater Skill

The Dockerfiles track a moving base (`php:8.X-fpm` for 8.2/8.4/8.5, Sury `php8.X-*` packages
on `debian:trixie` for 8.0/8.1), so a patch release needs **no code change**, only a rebuild
through CI. Read `AGENTS.md` first. This skill never edits files and never commits.

Argument: one or more versions (`8.5`, `8.4 8.5`), or none for all versions in `VERSIONS` of
`scripts/dockerhub_update.py`.

## Hard rules
- **Never `docker push` locally.** A local push is amd64-only and overwrites the multi-arch
  `latest`. Publishing goes through `.github/workflows/docker-publish.yml` only.
- The workflow has no version input: a manual run rebuilds every version, like the weekly
  run. That is fine (same minor version, `latest` only). Tell the user.
- Do not start a second run while one is `queued`/`in_progress`; watch the existing one.
- Pin nothing. Do not "update" by editing a `FROM` line to a patch tag.

## Step 1 — Compare upstream with published
Run from the repo root (Bash). Derive the version list from `VERSIONS` (never hardcode it,
so a newly added version is not skipped) and split it by base: a `FROM php:` Dockerfile is an
official-image version, a `FROM debian:` one is a Sury version.

```bash
all=$(python -c "import re;print(' '.join(re.findall(r'\"(8\.\d+)\"', re.search(r'^VERSIONS = \[.*\]', open('scripts/dockerhub_update.py').read(), re.M).group(0))))")
official=""; sury=""
for v in $all; do
  if grep -q '^FROM php:' $v/Dockerfile; then official="$official $v"; else sury="$sury $v"; fi
done
echo "official:$official  sury:$sury"
```
Narrow both lists to the requested versions if the user named any.

For the official-image versions:

```bash
for v in $official; do
  up=$(docker buildx imagetools inspect php:$v-fpm --format '{{json .Image}}' | grep -o 'PHP_VERSION=[0-9.]*' | head -1)
  pub=$(docker buildx imagetools inspect yohannaftali/php$v-fpm:latest --format '{{json .Image}}' | grep -o 'PHP_VERSION=[0-9.]*' | head -1)
  echo "$v upstream=${up#*=} published=${pub#*=}"
done
```

If `published` comes back empty (the label is not inherited), fall back to
`docker run --rm --pull always yohannaftali/php$v-fpm php -r 'echo PHP_VERSION;'`.

For the Sury versions (currently 8.0/8.1; version is the Debian package revision, e.g. `8.1.34-9`):

```bash
curl -fsSL https://packages.sury.org/php/dists/trixie/main/binary-amd64/Packages.gz | gunzip \
  | awk '/^Package: php8\.[0-9]+-common$/{p=$2} p&&/^Version:/{print p, $2; p=""}' | sort -V
for v in $sury; do
  docker run --rm --pull always yohannaftali/php$v-fpm dpkg-query -W -f '${Package} ${Version}\n' php$v-common
done
```

Report a table: version, upstream, published, needs update (yes/no). Also show the last
publish run: `gh run list --workflow docker-publish.yml -L 3`.

If nothing is behind, say so and stop (unless the user explicitly asks to rebuild anyway).
If the user named a target patch (e.g. "8.5.13") and upstream does not have it yet, stop
and say so; do not build.

## Step 2 — Smoke test locally before publishing
CI's build is not a test, so a broken upstream patch would otherwise reach `latest`. For each
version that needs an update, build locally (native platform only, **never pushed**) and
check it. `docker info` must work; if not, stop and say so (no publish without a pass).

```bash
docker build --pull -f $v/Dockerfile -t php-update:$v .
docker run --rm php-update:$v php -v                    # expect the upstream patch from Step 1
docker run --rm php-update:$v php-fpm -t                # config is valid
docker run --rm php-update:$v php -m | grep -Ei '^(redis|imagick|igbinary)$'   # extensions load
docker run --rm php-update:$v composer --version
```
For Sury versions also check `dpkg-query -W php$v-common` matches Step 1. Any failure: stop,
do not publish, report the command and its output. Afterwards remove the `php-update:*`
images.

## Step 3 — Trigger the publish
Pushing to `main` or triggering the workflow publishes to Docker Hub. The user asking to
update/publish is the confirmation; otherwise ask first.

```bash
gh run list --workflow docker-publish.yml -L 1 --json databaseId,status   # reuse if active
gh workflow run docker-publish.yml --ref main
sleep 5; gh run list --workflow docker-publish.yml -L 1 --json databaseId,status,url
```

Give the user the run URL.

## Step 4 — Wait
Run in the background so the user is not blocked (about 6 minutes):

```bash
gh run watch <id> --exit-status --interval 30 > /dev/null; echo "exit=$?"
gh run view <id> --json conclusion,jobs -q '.conclusion, (.jobs[] | "\(.name): \(.conclusion)")'
```

If any `build`/`merge` job for a requested version failed, show the failing step
(`gh run view <id> --log-failed | tail -50`) and stop. Other versions failing does not block
the requested one (`merge` runs with `if: !cancelled()`), but report it.

## Step 5 — Verify on Docker Hub
For each requested version:

```bash
docker buildx imagetools inspect yohannaftali/php$v-fpm:latest | grep -i platform   # linux/amd64 AND linux/arm64
docker run --rm --pull always yohannaftali/php$v-fpm php -v                         # new patch version
docker run --rm yohannaftali/php$v-fpm php-fpm -t
```

For Sury versions, check the `php$v-common` package version matches Sury's from Step 1.
If `latest` lost a platform, restore it per AGENTS.md
(`docker buildx imagetools create -t <repo>:latest <repo>@<multi-arch digest>`) only after
asking.

## Step 6 — Report
Version before -> after for each requested version, platforms present, run URL, and any
other version that failed. A routine rebuild is not a structural change: do not touch
`AGENTS.md` or `CHANGE_HISTORY.md` for it, except a security release worth recording (e.g.
a CVE fix), which gets a short dated `CHANGE_HISTORY.md` entry after asking.
