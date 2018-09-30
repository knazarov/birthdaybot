from database import db
from sqlalchemy import Column, Integer, String, DateTime, \
    ForeignKey, Boolean, Text, UniqueConstraint, event, Numeric, \
    Date
from sqlalchemy.orm import backref, relation
from sqlalchemy.sql import union
from sqlalchemy_utils import aggregated
import sqlalchemy as sa
import flask_security

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

    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relation('Role', secondary=roles_users,
                     backref=backref('users', lazy='dynamic'))
    birthday = Column(Date)

    def __str__(self):
        return '<User id=%s name=%s, balance=%s>' % (self.id, self.first_name, self.balance)

    participates = Column(Boolean(), default=True, nullable=False)

    @aggregated('payments', Column(Numeric))
    def payment_sum(self):
        return sa.func.sum(Payment.amount)

    @aggregated('deposits', Column(Numeric))
    def deposit_sum(self):
        print("agg:", sa.func.sum(Deposit.amount))
        return sa.func.sum(Deposit.amount)

    @property
    def balance(self):
        print("Deposit: ", self.deposit_sum)
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
