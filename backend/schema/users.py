import re
import phonenumbers

from marshmallow import validate, validates, ValidationError, fields, validates_schema

from app import ma
from models.user import User


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(dump_only=True)
    email = ma.String(dump_only=True)
    is_verified = ma.Boolean(dump_only=True)


class LoginSchema(ma.SQSQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(required=True)
    password = ma.String(required=True)


class RegisterSchema(ma.SQSQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(required=True)
    password = ma.String(required=True)
    confirm_password = ma.String(required=True)
