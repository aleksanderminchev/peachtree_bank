from flask import Blueprint, abort, request
from apifairy import authenticate, body, response, other_responses

from models.user import User
from models.token import Token
from schema.users import UserSchema, LoginSchema, RegisterSchema
from schema.tokens import TokenSchema
from auth import token_auth
from app import db
from utils.utils import get_date

users = Blueprint("users", __name__)


@users.route("/login", methods=["POST"])
@body(LoginSchema)
def login(args):
    username = args.get("username", None)
    password = args.get("password", None)
    user = User.get_user_by_username(username)
    if user is None:
        return {"error": "No user found"}, 404
    print(user.verify_password(password))
    result = user.verify_password(password)
    if not result:
        return {"error": "Incorrect password"}, 403
    token = Token(user=user.uid)
    db.session.add(token)
    db.session.commit()
    raw_token = token.generate_tokens()
    return Token.token_response(raw_token)


@users.route("/get_user", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema)
def get_user(args):
    user = token_auth.current_user()
    if user is None:
        return {"error": "No user is found"}, 404
    return user


@users.route("/register", methods=["POST"])
@body(RegisterSchema)
@response(UserSchema)
def register():
    """
    Register a new user
    Expected JSON payload:
    {
        "username": "string",
        "password": "string",
        "confirm_password": "string",
        "email": "string",
        "first_name": "string" (optional),
        "last_name": "string" (optional)
    }
    """
    try:
        # Get validated data from the body decorator
        validated_data = request.validated_data

        # Extract fields
        username = validated_data.get("username")
        password = validated_data.get("password")
        email = validated_data.get("email")
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        # Create new user instance
        new_user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        # Return the created user (will be serialized by @response decorator)
        return new_user

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@users.route("/tokens", methods=["PUT"])
@response(TokenSchema, description="Newly issued access and refresh tokens")
def refresh(args):
    """Refresh an access token"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return {"error": "Unauthorized"}, 403
    # Get token object
    token_obj = Token.get_token_by_refresh_token(refresh_token)
    if not token_obj:
        return {"error": "Invalid refresh token"}, 403

    # Check if token is expired
    if get_date() >= token_obj.refresh_expiration:
        return {"error": "Refresh token expired"}, 403

    # Verify the user still exists
    user = User.query.get(token_obj.user_id)
    if not user:
        return {"error": "User not found"}, 403

    # Issue new tokens for this user
    return Token.token_response(refresh_token)


@users.route("/forgot_password", methods=["POST"])
def forgot_password():
    pass


@users.route("/update_user", methods=["PUT"])
def update():
    pass
