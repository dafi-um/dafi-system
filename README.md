DAFI Website
============

## Deployment

Follow these steps after pulling from the repo:

```
python manage.py collectstatic
```

### Nginx

Here's the basic configuration for Nginx:

```
upstream django {
  server unix:///PATH_TO_PROJECT/web_dafi.sock;
}

server {
  listen 80 default_server;
  listen [::]:80 default_server;

  index index.html;

  server_name YOUR_DOMAIN;

  sendfile on;

  ###
  # GZIP
  ###
  gzip              on;
  gzip_http_version 1.0;
  gzip_proxied      any;
  gzip_min_length   500;
  gzip_disable      "MSIE [1-6]\.";
  gzip_types        text/plain text/xml text/css
                    text/comma-separated-values
                    text/javascript
                    application/x-javascript
                    application/atom+xml;

  ###
  # Locations
  ###
  location / {
    include    uwsgi_params;
    uwsgi_pass django;

    proxy_redirect   off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Host $server_name;
  }

  location ^~ /static {
    alias /PATH_TO_PROJECT/website/static;
  }
}
```

### UWSGI

Here's the basic configuration for UWSGI:

```ini
[uwsgi]

# Django-related settings
chdir           = /PATH_TO_PROJECT/website
module          = website.wsgi
home            = /PATH_TO_PROJECT/venv

# process-related settings
master          = true
processes       = 10
socket          = /PATH_TO_PROJECT/web_dafi.sock
# 666 if the user running uwsgi is not in the www-data group else 664
chmod-socket    = 666
vacuum          = true
```

To run the daemon just execute:

```bash
venv/bin/uwsgi --ini app_uwsgi.ini --uid www-data --gid www-data --daemonize uwsgi_webdafi.log --pidfile uwsgi_webdafi.pid
```
