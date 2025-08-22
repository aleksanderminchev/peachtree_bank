from flask import current_app, request, abort, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import time
from sqlalchemy.orm import validates
from app import db
from models.token import Token
from services.email import send_email
from utils.utils import get_date

from models.basemodel import BaseModel


class User(BaseModel):

    __tablename__ = "users"

    # general
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    is_verified = db.Column(
        db.Boolean,
        default=False,
    )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):  # Hashes the password
        self.password_hash = generate_password_hash(password)

    @validates("email")
    def validate_email(self, key, email):
        if not isinstance(email, str):
            raise ValueError("invalid email")
        if len(email) < 6 or len(email) > 120:
            raise ValueError("invalid email")

        return email

    @validates("username")
    def validate_username(self, key, username):
        if not isinstance(username, str):
            raise ValueError("invalid email")
        if len(username) < 6 or len(username) > 120:
            raise ValueError("invalid email")

        return username

    def verify_password(self, password):  # Verifies the hashed password
        return check_password_hash(self.password_hash, password)
