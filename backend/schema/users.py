from app import ma
from models.user import User
import re
from marshmallow import Schema, fields, validates, ValidationError, post_load

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

    @validates("username")
    def validate_username(self, value):
        # Check if username contains only alphanumeric characters and underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )

        # Check if username already exists
        existing_user = User.query.filter_by(username=value).first()
        if existing_user:
            raise ValidationError("Username already exists")

    @validates("email")
    def validate_email(self, value):
        # Check if email already exists
        existing_user = User.query.filter_by(email=value).first()
        if existing_user:
            raise ValidationError("Email already registered")

    @validates("password")
    def validate_password(self, value):
        # Password strength validation
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(
                "Password must contain at least one special character"
            )

    @post_load
    def validate_password_match(self, data, **kwargs):
        if data["password"] != data["confirm_password"]:
            raise ValidationError(
                "Passwords do not match", field_name="confirm_password"
            )
        return data
