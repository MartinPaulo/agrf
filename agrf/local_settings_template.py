# This file shows the settings that can be placed in local_settings.py
# local_settings.py is a way for us to have machine specific information
# if (any)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# Debug defaults to False
DEBUG = False
# Hence the following allowed hosts will stop the server from running...
# So you need to set it to be whatever server the software is running on
ALLOWED_HOSTS = []

# These are the people that email will flow to...
ADMINS = (
    ('One Admin', 'one.admin@somewhere.edu.au'),
    ('Two Admin', 'two.admin@somewhere.edu.au')
)

MANAGERS = (
    ('One Manager', 'one.manager@somewhere.edu.au'),
    ('Two Manager', 'two.manager@somewhere.edu.au')
)

# enable and set if you don't want email to come from root@localhost
# SERVER_EMAIL = 'agrf@nectar.org.au'
# DEFAULT_FROM_EMAIL = 'agrf@nectar.org.au'

# DATABASES = {
#     'default': {
#         # 'ENGINE': 'django.db.backends.sqlite3',
#         # 'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
#     }
# }


# The OpenID urls (note slash at end of the TRUST ROOT...
TRUST_ROOT = 'http://127.0.0.1/'
RETURN_TO_URL = TRUST_ROOT + 'gs_login/?is_return=true'
LOGOUT_TAIL = 'openIdProvider?_action=logout&logout_return_to=' + TRUST_ROOT

# where the files come from..
BASE_DIRECTORY = ''

ENVIRONMENT_NAME='Production'
ENVIRONMENT_COLOR='red'

# add our pam backend to the list of authentication backends being used.
AUTHENTICATION_BACKENDS = [
    'pam_auth.backend.PamBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# The number of days a file will live for on the AGRF servers before being
# removed/deleted
DAYS_FILES_LIVE_FOR = 30


# set to wherever you want your static files to live
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# STATIC_ROOT = '/var/www/static'

# If running in debug mode, this will connect to the python debugging server
# launched as follows:
# python -m smtpd -n -c DebuggingServer localhost:1025
# The debugging server will simply print all email sent by the application to
# the command line.
if DEBUG:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'debug@agrf.uom.edu.au'
