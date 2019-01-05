import os

def read_config(app):
    app.config.from_object('config')

    if os.path.exists('.env'):
        app.config.from_pyfile(os.path.join(
            os.path.dirname(app.instance_path), '.env'))

    if os.getenv('BOT_TOKEN'):
        app.config['BOT_TOKEN'] = os.getenv('BOT_TOKEN')

    if os.getenv('SERVER_NAME'):
        app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')

    if os.getenv('BIRTHDAY_TOKEN'):
        app.config['BIRTHDAY_TOKEN'] = os.getenv('BIRTHDAY_TOKEN')

    if os.getenv('CARD_NUMBERS'):
        app.config['CARD_NUMBERS'] = os.getenv('CARD_NUMBERS')

    app.config['CARD_NUMBERS'] = app.config['CARD_NUMBERS'].split(",")

    if os.getenv('ADMIN_ID'):
        app.config['ADMIN_ID'] = os.getenv('ADMIN_ID')

    if os.getenv('PREFERRED_URL_SCHEME'):
        app.config['PREFERRED_URL_SCHEME'] = os.getenv('PREFERRED_URL_SCHEME')

    if os.getenv('DATABASE_URL'):
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres:'):
            database_url = database_url.replace('postgres:', 'postgresql+psycopg2:', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    elif app.config['DATABASE_URL']:
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']

    if os.getenv('REDIS_URL'):
        app.config['REDIS_URL'] = os.getenv('REDIS_URL')

    if app.config.get('REDIS_URL', None):
        app.config['CELERY_BROKER_URL'] = app.config['REDIS_URL']
        app.config['CELERY_RESULT_BACKEND'] = app.config['REDIS_URL']

    if os.getenv('MAIL_PASSWORD'):
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    if os.getenv('DEBUG'):
        app.config['DEBUG'] = os.environ.get('DEBUG') == 'True'

    if os.getenv('TEMPLATE_DEBUG'):
        app.config['TEMPLATE_DEBUG'] = os.environ.get('TEMPLATE_DEBUG') == 'True'

    if os.getenv('ERRBIT_PROJECT_ID'):
        app.config['PYBRAKE'] = {
            'project_id': int(os.getenv('ERRBIT_PROJECT_ID')),
            'project_key': os.getenv('ERRBIT_PROJECT_KEY'),
            'host': os.getenv('ERRBIT_HOST'),
            'environment': os.getenv('ERRBIT_ENVIRONMENT')
        }

    if os.getenv('GOOGLE_CLIENT_ID'):
        app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

    if os.getenv('GOOGLE_CLIENT_SECRET'):
        app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
