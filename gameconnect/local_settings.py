# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': 'coderslab',
        'USER': 'postgres',
        'PORT': 5432
    }
}

# mailchimp api key: f80c5cfffd8a1452b5bfa39c402ff28b-us21

MAILCHIMP_API_KEY = 'f80c5cfffd8a1452b5bfa39c402ff28b-us21'
MAILCHIMP_SERVER_PREFIX = 'us21'