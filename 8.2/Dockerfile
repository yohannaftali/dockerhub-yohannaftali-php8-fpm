FROM php:8.2-fpm

LABEL org.opencontainers.image.title="php8.2-fpm" \
      org.opencontainers.image.description="PHP 8.2-FPM with common extensions, redis, imagick, igbinary, sendmail and Composer" \
      org.opencontainers.image.authors="Yohan Naftali" \
      org.opencontainers.image.source="https://github.com/yohannaftali/dockerhub-yohannaftali-php8-fpm"

ENV TZ=Asia/Jakarta
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    build-essential \
    libcurl4 \
    libcurl4-openssl-dev \
    libfreetype-dev \
    libgd-dev \
    libicu-dev \
    libjpeg62-turbo-dev \
    jpegoptim \
    libpng-dev \
    libwebp-dev \
    optipng \
    pngquant \
    libmagickwand-dev \
    libmcrypt-dev \
    libonig-dev \
    libpq-dev \
    libxml2-dev \
    libxml2 \
    libxml2-utils \
    libpcre2-dev \
    libzip-dev \
    libxslt1-dev \
    libssl-dev \
    libldap2-dev \
    libldb-dev \
    libldap-common \
    libsasl2-dev \
    libsocket++-dev \
    zlib1g-dev \
    gifsicle \
    curl \
    wget \
    openssl \
    sendmail \
    nano \
    zip \
    unzip \
    git

RUN docker-php-ext-configure gd --enable-gd --with-freetype=/usr/lib/ --with-jpeg=/usr/lib/ --with-webp=/usr
RUN docker-php-ext-configure pdo_mysql --with-pdo-mysql=mysqlnd
RUN docker-php-ext-configure mysqli --with-mysqli=mysqlnd
RUN docker-php-ext-configure intl
RUN docker-php-ext-configure zip
RUN docker-php-ext-install -j$(nproc) \
    gd \
    mysqli \
    pdo \
    pdo_mysql \
    zip \
    soap \
    iconv \
    bcmath \
    mbstring \
    pcntl \
    exif \
    intl \
    curl \
    ctype \
    simplexml \
    xml \
    ldap \
    sockets

RUN pecl install imagick
RUN pecl install igbinary
RUN pecl install redis
RUN docker-php-ext-enable \
    mysqli \
    pdo \
    pdo_mysql \
    imagick \
    igbinary \
    redis

RUN echo "sendmail_path=/usr/sbin/sendmail -t -i" >> /usr/local/etc/php/conf.d/sendmail.ini
RUN sed -i '/#!\/bin\/sh/aservice sendmail restart' /usr/local/bin/docker-php-entrypoint
RUN sed -i '/#!\/bin\/sh/aecho "$(hostname -i)\t$(hostname) $(hostname).localhost" >> /etc/hosts' /usr/local/bin/docker-php-entrypoint

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer
