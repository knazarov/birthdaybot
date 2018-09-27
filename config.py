from celery.schedules import crontab

SECRET_KEY = "ilikerandompasswords"
BOT_TOKEN = None
DATABASE_URL = 'postgresql://postgres@localhost/postgres'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
DEBUG = False
TEMPLATE_DEBUG = False
TEMPLATE_AUTO_RELOAD = True
SECURITY_USER_IDENTITY_ATTRIBUTES = "id"


#SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_LOGIN_URL = "/security_login"

DEBUG_TB_INTERCEPT_REDIRECTS = False

ADMIN_ID = ""


CARD_NUMBERS = []


CELERY_SCHEDULE = {
    'weekly_stats': {
        'task': 'nudge',
        'schedule': crontab(hour=21, minute=0, day_of_week='*')
    },
}
