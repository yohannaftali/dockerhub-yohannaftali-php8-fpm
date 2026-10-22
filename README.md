# yohannaftali/php8-fpm images

[PHP 8.x-FPM](https://hub.docker.com/_/php) images with common extensions, redis, imagick, igbinary, sendmail and Composer. The container clock is set to **Asia/Jakarta (WIB, UTC+7)**; PHP itself stays on UTC (see Overview).

One image per PHP version, each in its own Docker Hub repository:

| Docker Hub repository | PHP | Pull |
| --- | --- | --- |
| [`yohannaftali/php8.0-fpm`](https://hub.docker.com/r/yohannaftali/php8.0-fpm) | 8.0 | `docker pull yohannaftali/php8.0-fpm` |
| [`yohannaftali/php8.1-fpm`](https://hub.docker.com/r/yohannaftali/php8.1-fpm) | 8.1 | `docker pull yohannaftali/php8.1-fpm` |
| [`yohannaftali/php8.2-fpm`](https://hub.docker.com/r/yohannaftali/php8.2-fpm) | 8.2 | `docker pull yohannaftali/php8.2-fpm` |
| [`yohannaftali/php8.4-fpm`](https://hub.docker.com/r/yohannaftali/php8.4-fpm) | 8.4 | `docker pull yohannaftali/php8.4-fpm` |
| [`yohannaftali/php8.5-fpm`](https://hub.docker.com/r/yohannaftali/php8.5-fpm) | 8.5 | `docker pull yohannaftali/php8.5-fpm` |

- Source code (Dockerfile, build workflow, scripts): <https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm>
- Issues and feature requests: <https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm/issues>

> **Note:** PHP 8.0 and 8.1 are end-of-life and PHP 8.2 receives security fixes only. PHP 8.4 and 8.5 are actively supported. There is no 8.3 image. Rebuilding weekly picks up whatever the official `php` image still publishes for each version, nothing more.

## Use these images

No build needed. Pull a prebuilt image straight from Docker Hub, or reference it in your `docker-compose.yml`:

```yaml
services:
  php:
    image: yohannaftali/php8.2-fpm:latest
```

## Overview

Each image is built `FROM php:<version>-fpm` and adds:

- **Timezone**: `TZ=Asia/Jakarta` for the operating system (`date`, logs, cron). PHP's `date.timezone` is intentionally left at its default, UTC, so applications stay timezone-agnostic. Set `date_default_timezone_set()` or `date.timezone` yourself if you need local time.
- **Extensions**: `gd` (freetype, jpeg, webp), `mysqli`, `pdo`, `pdo_mysql`, `zip`, `opcache`, `soap`, `iconv`, `bcmath`, `mbstring`, `pcntl`, `exif`, `intl`, `curl`, `ctype`, `simplexml`, `xml`, `ldap`, `sockets`, plus `imagick`, `igbinary` and `redis` from PECL. Xdebug is not included (production images).
- **Composer** (latest) at `/usr/local/bin/composer`.
- **Mail**: `sendmail` configured as `sendmail_path`; the entrypoint restarts it on container start.
- **Hosts entry**: the entrypoint appends the container's IP and hostname to `/etc/hosts` (needed by sendmail).
- **Tools**: `git`, `nano`, `wget`, `curl`, `openssl`, `zip`, `unzip`, and `jpegoptim`, `optipng`, `pngquant`, `gifsicle`.

## Tags

Each repository has a single tag, `latest`, rebuilt weekly from `php:<version>-fpm`.

## Quick start

```yaml
services:
  php:
    image: yohannaftali/php8.2-fpm:latest
    restart: unless-stopped
    volumes:
      - ./app:/var/www/html
    expose:
      - "9000"

  web:
    image: nginx:stable
    ports:
      - "8080:80"
    volumes:
      - ./app:/var/www/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - php
```

Verify an image:

```bash
docker run --rm yohannaftali/php8.2-fpm php -v
docker run --rm yohannaftali/php8.2-fpm date +%Z                                  # WIB (OS)
docker run --rm yohannaftali/php8.2-fpm php -r 'echo date_default_timezone_get();' # UTC (by design)
docker run --rm yohannaftali/php8.2-fpm php -m
docker run --rm yohannaftali/php8.2-fpm composer --version
```

## Build (maintainers)

```bash
docker login

# one version
docker build --build-arg PHP_VERSION=8.2 -t yohannaftali/php8.2-fpm:latest .
docker push yohannaftali/php8.2-fpm:latest
```

Multi-arch (amd64 + arm64):

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  --build-arg PHP_VERSION=8.2 \
  -t yohannaftali/php8.2-fpm:latest --push .
```

## Automated publishing

`.github/workflows/docker-publish.yml` builds and pushes all versions in parallel on every push to `main`, weekly, and on manual dispatch. It also syncs this README to each Docker Hub **overview** and sets each short **description**.

Required GitHub repository secrets:

| Secret | Value |
| --- | --- |
| `DOCKERHUB_USERNAME` | `yohannaftali` |
| `DOCKERHUB_TOKEN` | Docker Hub access token with *Read, Write, Delete* scope |

### Adding a PHP version

1. Add the version to the `php` matrix in **both** jobs of the workflow, and to `VERSIONS` in `scripts/dockerhub_update.py`.
2. Add it to the table at the top of this README.
3. Create the Docker Hub repository `yohannaftali/php<version>-fpm` (or let the first push create it) and set its category.

## Maintaining the Docker Hub repositories

- **Overview**: synced from this `README.md` by the workflow.
- **Short description**: set in the workflow (`short-description`), max 100 characters.
- **Manual sync / status**: see [Maintenance scripts](#maintenance-scripts).
- **Category**: not exposed through the API; set manually in *Repository → Settings → Categories* for each repository.

## Maintenance scripts

Helper scripts in `scripts/` manage the Docker Hub repositories from your machine. They need [uv](https://docs.astral.sh/uv/) and a `.env` file (copy `.env.example`) with `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`. There are no other dependencies.

| Command | Action |
| --- | --- |
| *(none)* / `sync [repo]` | Push `README.md` as the overview and set the short description (all repos, or one) |
| `status [repo]` | Show description, categories, pull and star counts |
| `tags [repo]` | List tags with last update and size |
| `delete-tag <repo> <tag>` | Delete a tag |

Bash:

```bash
./scripts/dockerhub-update.sh                  # sync all
./scripts/dockerhub-update.sh status php8.2-fpm
./scripts/dockerhub-update.sh tags
```

PowerShell:

```powershell
.\scripts\dockerhub-update.ps1                  # sync all
.\scripts\dockerhub-update.ps1 status php8.2-fpm
.\scripts\dockerhub-update.ps1 tags
```

Both wrappers call `scripts/dockerhub_update.py` through `uv run`.

## Source and contributing

The Dockerfile, GitHub Actions workflow and maintenance scripts live at <https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm>. Open an issue there to report a problem or request a PHP version.

## License

The Dockerfile in this repository is provided as-is. PHP is licensed under the PHP License; see the [official image](https://hub.docker.com/_/php) for details.
