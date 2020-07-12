# make models
# range inputs

from create_app import app
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy(app)

# make models
# range inputs
# radio
class derive_enum(Enum):
    def __str__(self):
        return str(self.value)

    def __iter__(self):
        return ((x.name, x.value) for x in Enum(self).__iter__())

class input_data(db.Model):
    __tablename__ = 'entry3'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    start = db.Column(db.Float())
    stop = db.Column(db.Float())
    steps = db.Column(db.Float())
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('input_data_list.id'))

class input_data1(db.Model):
    __tablename__ = 'entry1'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    val = db.Column(db.Float())
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('input_data_list.id'))

class radio_data(db.Model):
    __tablename__ = 'radio'
    id = db.Column(db.Integer(), primary_key=True)
    spec = db.Column(db.String(50))
    default = db.Column(db.String(50))
    # choices = db.Column(db.Array(db.String, dimensions=2))
    input_data_id = db.Column(
        db.Integer(), db.ForeignKey('radio_check_data_list.id'))

class check_data(radio_data):
    __tablename__ = 'check'

class input_data_list(db.Model):
    __tablename__ = 'input_data_list'
    id = db.Column(db.Integer(), primary_key=True)
    section = db.Column(db.String(50))

    values = db.relationship('input_data')
    values1 = db.relationship('input_data1')

class radio_check_data_list(db.Model):
    __tablename__ = 'radio_check_data_list'
    id = db.Column(db.Integer(), primary_key=True)

    section = db.Column(db.String(50))

    radio = db.relationship('radio_data')
    check = db.relationship('check_data')
