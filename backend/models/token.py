from flask import current_app, abort
from app import db
import jwt
from models.basemodel import BaseModel
from datetime import datetime, timedelta
import secrets
from utils.utils import get_date
import secrets
import hashlib
from werkzeug.http import dump_cookie


class Token(BaseModel):
    __tablename__ = "tokens"

    uid = db.Column(db.Integer, primary_key=True)
    refresh_token = db.Column(db.String(64), nullable=False, index=True, unique=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), index=True)

    user = db.relationship("User", backref="tokens")

    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id

    @staticmethod
    def generate_tokens():
        """Generate  tokens"""

        # Step 1: generate raw random token
        refresh_token_raw = secrets.token_urlsafe(32)

        # Step 2: hash it for DB storage (SHA-256)
        refresh_token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()

        return refresh_token_raw, refresh_token_hash

    def set_refresh_token_date(self, refresh_days=30):
        now = get_date()
        self.refresh_expiration = now + timedelta(days=refresh_days)
        db.session.commit()

    @staticmethod
    def get_token_by_refresh_token(candidate_token: str):
        """
        Get token object by refresh token hash, regardless of expiration.
        Returns the token object if found, None if not found.
        """
        candidate_hash = hashlib.sha256(candidate_token.encode()).hexdigest()
        return Token.query.filter(Token.refresh_token == candidate_hash).first()

    def get_access_jwt(self):
        """Generate JWT for access token"""
        try:
            print("secret_ley", current_app.config["SECRET_KEY"])
            return jwt.encode(
                {
                    "token": secrets.token_urlsafe(),
                    "exp": (get_date() + timedelta(minutes=15)).timestamp(),
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256",
            )
        except Exception as e:
            raise ValueError(f"Failed to encode access token: {str(e)}")

    def get_refresh_jwt(self):
        """Generate JWT for refresh token"""
        try:
            return jwt.encode(
                {
                    "token": self.refresh_token,
                    "user_id": self.user_id,
                    "exp": self.refresh_expiration.timestamp(),
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256",
            )
        except Exception as e:
            raise ValueError(f"Failed to encode refresh token: {str(e)}")

    @classmethod
    def decode_access_token(cls, jwt_token=None):
        """
        Decode access token JWT

        Args:
            jwt_token (str, optional): JWT to decode. If None, generates from access_token

        Returns:
            dict: Decoded token payload

        Raises:
            jwt.ExpiredSignatureError: Token is expired
            jwt.InvalidTokenError: Token is invalid
        """

        return jwt.decode(
            jwt_token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )

    @classmethod
    def verify_access_token(cls, access_token):
        from models.user import User

        token = Token.decode_access_token(access_token)
        if not token:
            return None

        if not token["user_id"]:
            return None
        if not (token["exp"] > datetime.utcnow()):
            return None
        user = User.get_user_by_id(token["user_id"])

        return user

    @classmethod
    def find_by_refresh_token(cls, refresh_token):
        """Find token by refresh token value"""
        return cls.query.filter_by(refresh_token=refresh_token).first()

    @staticmethod
    def token_response(token_db, token_raw):
        headers = {}
        domain = None
        if current_app.config["ENV_NAME"] == "production":
            domain = "fake_domain.com"

        headers["Set-Cookie"] = dump_cookie(
            "refresh_token",
            token_raw,
            secure=True,
            httponly=True,
            samesite="none",
            domain=domain,
        )
        access_token = token_db.get_access_jwt()
        print("access_token", access_token)
        return (
            {
                "access_token": access_token,
            },
            200,
            headers,
        )
