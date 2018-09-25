#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database(app):
    db.init_app(app)
    db.app = app

    # Assuming that gevent monkey patched the builtin
    # threading library, we're likely good to use
    # SQLAlchemy's QueuePool, which is the default
    # pool class.  However, we need to make it use
    # threadlocal connections
    #
    #
    db.engine.pool._use_threadlocal = True
