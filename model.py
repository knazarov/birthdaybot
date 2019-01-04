from database import db
from sqlalchemy import Column, Integer, String, DateTime, \
    ForeignKey, Boolean, Text, UniqueConstraint, event, Numeric, \
    Date
from sqlalchemy.orm import backref, relation
from sqlalchemy.sql import union
from sqlalchemy_utils import aggregated
import sqlalchemy as sa
import flask_security
import flask

roles_users = db.Table(
    'roles_users',
    Column('user_id', Integer(), ForeignKey('user.id')),
    Column('role_id', Integer(), ForeignKey('role.id')))


class Role(db.Model, flask_security.RoleMixin):
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __str__(self):
        return '<Role %s>' % self.name


class User(db.Model, flask_security.UserMixin):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    phone = Column(String(255))

    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relation('Role', secondary=roles_users,
                     backref=backref('users', lazy='dynamic'))
    approved = Column(Boolean(), nullable=False)

    birthday = Column(Date)

    def full_name(self):
        name = []

        if self.first_name:
            name.append(self.first_name)

        if self.last_name:
            name.append(self.last_name)

        return ' '.join(name)


    def __str__(self):
        return '<User id=%s name=%s, balance=%s>' % (self.id, self.full_name(), self.balance)

    participates = Column(Boolean(), default=True, nullable=False)
    celebrates = Column(Boolean(), default=True, nullable=False)

    @aggregated('payments', Column(Numeric))
    def payment_sum(self):
        return sa.func.sum(Payment.amount)

    @aggregated('deposits', Column(Numeric))
    def deposit_sum(self):
        #print("agg:", sa.func.sum(Deposit.amount))
        return sa.func.sum(Deposit.amount)

    @property
    def balance(self):
        deposit = self.deposit_sum or 0
        payment = self.payment_sum or 0
        return deposit - payment


class Birthday(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relation("User",
                    backref="birthdays",
                    foreign_keys=[user_id])

    gift = Column(Text)
    amount = Column(Numeric())


class Payment(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relation("User",
                    backref="payments",
                    foreign_keys=[user_id])
    birthday_id = Column(Integer, ForeignKey('birthday.id'), nullable=False)
    birthday = relation("Birthday",
                        backref="participations",
                        foreign_keys=[birthday_id])

    amount = Column(Numeric())


class Deposit(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relation("User",
                    backref="deposits",
                    foreign_keys=[user_id])
    amount = Column(Numeric())


def get_users():
    q = (User.query
         .filter(User.approved == True)
         .filter(User.participates == True))

    return q.all()


def get_celebrating():
    q = (User.query
         .filter(User.approved == True)
         .filter(User.participates == True)
         .filter(User.celebrates == True))

    return q.all()


def is_authorized(user_id):
    app = flask.current_app
    admin_id = int(app.config["ADMIN_ID"])

    if user_id == admin_id:
        return True

    user = User.query.get(user_id)

    if user is None:
        return False

    if not user.approved:
        return False

    return True


def is_admin(user_id):
    app = flask.current_app
    admin_id = int(app.config["ADMIN_ID"])

    return user_id == admin_id
