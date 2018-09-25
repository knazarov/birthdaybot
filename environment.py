import os

def read_config(app):
    app.config.from_object('config')

    if os.path.exists('.env'):
        app.config.from_pyfile(os.path.join(
            os.path.dirname(app.instance_path), '.env'))

    if os.getenv('SERVER_NAME'):
        app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')

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
        app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL')
        app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL')

    if os.getenv('MAIL_PASSWORD'):
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    if os.getenv('S3_URL'):
        app.config['S3_URL'] = os.environ.get('S3_URL')

    if os.getenv('S3_ACCESS_KEY'):
        app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')

    if os.getenv('S3_SECRET_KEY'):
        app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')

    if os.getenv('S3_BUCKET'):
        app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET')

    if os.getenv('S3_REGION'):
        app.config['S3_REGION'] = os.environ.get('S3_REGION')

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
