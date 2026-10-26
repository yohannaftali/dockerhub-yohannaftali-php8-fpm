# PHP 8.1 is EOL: the official php:8.1-fpm image gets no more security fixes (e.g. PHP2Shell,
# CVE-2026-109618/109619). Build on Debian with Ondřej Surý's backported packages instead and
# mimic the official image layout (php-fpm on :9000, docker-php-entrypoint, /var/www/html).
FROM debian:trixie

ARG PHP=8.1

LABEL org.opencontainers.image.title="php8.1-fpm" \
      org.opencontainers.image.description="PHP 8.1-FPM with common extensions, redis, imagick, igbinary, sendmail and Composer" \
      org.opencontainers.image.authors="Yohan Naftali" \
      org.opencontainers.image.source="https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm"

ENV TZ=Asia/Jakarta
ENV DEBIAN_FRONTEND=noninteractive
# Leading ":" keeps the package's conf.d and adds the official image's conf.d location
ENV PHP_INI_SCAN_DIR=:/usr/local/etc/php/conf.d

RUN apt-get update && apt-get install -y ca-certificates curl tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && curl -fsSLo /tmp/debsuryorg-archive-keyring.deb https://packages.sury.org/debsuryorg-archive-keyring.deb \
    && dpkg -i /tmp/debsuryorg-archive-keyring.deb && rm /tmp/debsuryorg-archive-keyring.deb \
    && echo "deb [signed-by=/usr/share/keyrings/debsuryorg-archive-keyring.gpg] https://packages.sury.org/php/ trixie main" \
       > /etc/apt/sources.list.d/php.list

RUN apt-get update && apt-get install -y \
    php${PHP}-fpm \
    php${PHP}-cli \
    php${PHP}-common \
    php${PHP}-bcmath \
    php${PHP}-curl \
    php${PHP}-gd \
    php${PHP}-intl \
    php${PHP}-ldap \
    php${PHP}-mbstring \
    php${PHP}-mysql \
    php${PHP}-opcache \
    php${PHP}-readline \
    php${PHP}-soap \
    php${PHP}-sqlite3 \
    php${PHP}-xml \
    php${PHP}-zip \
    php${PHP}-imagick \
    php${PHP}-igbinary \
    php${PHP}-redis \
    jpegoptim \
    optipng \
    pngquant \
    gifsicle \
    wget \
    openssl \
    sendmail \
    nano \
    zip \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Match the official image: no php.ini (built-in defaults), FPM in the foreground on :9000, logs to stderr
RUN rm -f /etc/php/${PHP}/cli/php.ini /etc/php/${PHP}/fpm/php.ini \
    && mkdir -p /run/php /usr/local/etc/php/conf.d /var/www/html \
    && chown www-data:www-data /var/www/html \
    && ln -s /usr/sbin/php-fpm${PHP} /usr/local/sbin/php-fpm \
    && sed -i 's|^error_log = .*|error_log = /proc/self/fd/2|' /etc/php/${PHP}/fpm/php-fpm.conf \
    && printf '%s\n' \
       '[global]' \
       'daemonize = no' \
       'log_limit = 8192' \
       '[www]' \
       'listen = 9000' \
       'access.log = /proc/self/fd/2' \
       'clear_env = no' \
       'catch_workers_output = yes' \
       'decorate_workers_output = no' \
       > /etc/php/${PHP}/fpm/pool.d/zz-docker.conf \
    && printf '%s\n' \
       '#!/bin/sh' \
       'set -e' \
       '' \
       '# first arg is `-f` or `--some-option`' \
       'if [ "${1#-}" != "$1" ]; then' \
       '	set -- php-fpm "$@"' \
       'fi' \
       '' \
       'exec "$@"' \
       > /usr/local/bin/docker-php-entrypoint \
    && chmod +x /usr/local/bin/docker-php-entrypoint

RUN echo "sendmail_path=/usr/sbin/sendmail -t -i" >> /usr/local/etc/php/conf.d/sendmail.ini
RUN sed -i '/#!\/bin\/sh/aservice sendmail restart' /usr/local/bin/docker-php-entrypoint
RUN sed -i '/#!\/bin\/sh/aecho "$(hostname -i)\t$(hostname) $(hostname).localhost" >> /etc/hosts' /usr/local/bin/docker-php-entrypoint

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

WORKDIR /var/www/html
ENTRYPOINT ["docker-php-entrypoint"]
STOPSIGNAL SIGQUIT
EXPOSE 9000
CMD ["php-fpm"]
