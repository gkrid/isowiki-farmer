FROM php:7.4-apache
MAINTAINER Grupa Konsultingowa RID <it@rid.pl>
ADD https://raw.githubusercontent.com/mlocati/docker-php-extension-installer/master/install-php-extensions /usr/local/bin/
RUN chmod +x /usr/local/bin/install-php-extensions && sync && install-php-extensions gd xdebug
COPY core_engines/latest /var/www/html
RUN chown -R www-data:www-data /var/www/html

# Install cron
RUN apt-get update && apt-get install -y tzdata cron
RUN cp /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && echo "Europe/Warsaw" > /etc/timezone
# RUN rm -rf /var/cache/apk/*

# Copy cron file to the cron.d directory
COPY cron /etc/cron.d/cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron

# Apply cron job
RUN crontab /etc/cron.d/cron

# Add a command to base-image entrypont script
RUN sed -i 's/^exec /service cron start\n\nexec /' /usr/local/bin/apache2-foreground

# Enable mod rewrite
RUN a2enmod rewrite

# Use the default production configuration
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"