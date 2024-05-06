from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from itsdangerous import *
from flask import *


db = SQLAlchemy()


class Registrations(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class UserProfileImage(db.Model):
    __tablename__ = "user_profile_images"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_extension = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)

class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    text = db.Column(db.String(255))

    def __init__(self, name, email, phone, text):
        self.name = name
        self.email = email
        self.phone = phone
        self.text = text