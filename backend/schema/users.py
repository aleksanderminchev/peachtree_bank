from app import ma
from models.user import User


class UserSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(dump_only=True)
    email = ma.String(dump_only=True)
    is_verified = ma.Boolean(dump_only=True)


class LoginSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(required=True)
    password = ma.String(required=True)


class RegisterSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True

    username = ma.String(required=True)
    password = ma.String(required=True)
    confirm_password = ma.String(required=True)
