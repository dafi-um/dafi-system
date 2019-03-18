DAFI Website
============

## Requirements

You'll need Python 3.6 or higher and a compatible version of pip to run this project.

## Deployment

Run the `deploy.sh` script to install all the dependencies using pip and configure the Django installation.

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
    alias /PATH_TO_PROJECT/static;
  }

  location ^~ /media {
    alias /PATH_TO_PROJECT/media;
  }
}
```

### UWSGI

To run the daemon execute:

```bash
venv/bin/uwsgi --ini app_socket.ini --uid www-data --gid www-data --daemonize uwsgi_webdafi.log --pidfile uwsgi_webdafi.pid
```
