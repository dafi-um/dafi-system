Sistemas Digitales de DAFI
==========================

## Requisitos y dependencias

Es necesario Python 3.9 o más reciente, y una versión compatible de pip.

Las dependencias de Python se pueden instalar con pip: `pip install -r requirements.txt`

Para ejecutar el bot es necesario instalar [ZBar](http://zbar.sourceforge.net/).

## Despliegue

El proyecto utiliza `staticfiles` de Django, por lo cual es necesario servir el directorio `static` en la ruta `/static`. Para agrupar todos los ficheros estáticos se debe ejecutar: `python manage.py collectstatic`.

### Variables de entorno

Todas las variables de entorno se pueden configurar en un fichero `.env` en el raíz del proyecto. Se proporciona un fichero de ejemplo: `.env.example`.

Para desarrollo es posible lanzar el proyecto solamente estableciendo `DEBUG=on`.

Nombre | Tipo | Descripción | Valor por defecto
---|---|---|---
`DEBUG` | booleana | Activa el [modo de depuración](https://docs.djangoproject.com/en/3.2/ref/settings/#debug) de Django | `False`
`SECRET_KEY` | texto | [Clave secreta](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key) de Django | `my-random-secret-key`
`ALLOWED_HOSTS` | lista de texto | Lista de [hosts admitidos](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts) en producción | `[]`
`DB_URL` | URL | URL de la base de datos por defecto ([más info](https://docs.djangoproject.com/en/3.2/ref/settings/#databases)) | `sqlite:///db.sqlite3`
`ADMINS` | lista de texto | Lista de [direcciones de e-mail de los administradores](https://docs.djangoproject.com/en/3.2/ref/settings/#admins) | `[]`
`EMAIL_FROM` | texto | [Dirección de e-mail](https://docs.djangoproject.com/en/3.2/ref/settings/#default-from-email) para envío de correos | `DAFI <dafi@um.es>`
`EMAIL` | URL | URL de la [configuración del correo electrónico](https://docs.djangoproject.com/en/3.2/ref/settings/#email) - solamente se utiliza cuando `DEBUG` es `False` | -
`BOT_TOKEN` | texto | Token del bot de Telegram | `''`
`STRIPE_PK` | texto | Clave pública de Stripe | `''`
`STRIPE_SK` | texto | Clave secreta de Stripe | `''`
`FIUMCRAFT_WHITELIST_ENDPOINT` | URL | URL del endpoint de la API de Fiumcraft | `''`
`FIUMCRAFT_WHITELIST_TOKEN` | texto | Token para la API de Fiumcraft | `''`
