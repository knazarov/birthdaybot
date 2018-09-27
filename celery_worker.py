#!/usr/bin/env python
from app import app, celery

app.app_context().push()
