from flask import current_app
from app import db
import jwt
from models.basemodel import BaseModel
from datetime import datetime, timedelta
import secrets
from utils.utils import get_date


class Token(BaseModel):
    __tablename__ = "tokens"

    uid = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True, unique=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True, unique=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), index=True)

    user = db.relationship("User", back_populates="tokens")

    def __init__(self, user_id, access_hours=1, refresh_days=30, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        # Set expiration times automatically
        now = datetime.utcnow()
        self.access_expiration = now + timedelta(hours=access_hours)
        self.refresh_expiration = now + timedelta(days=refresh_days)

        # Generate tokens during creation
        self._generate_tokens()

    def _generate_tokens(self):
        """Generate both raw tokens and JWTs"""
        import secrets

        self.access_token_raw = secrets.token_urlsafe(32)
        self.refresh_token_raw = secrets.token_urlsafe(32)

        self.access_token_jwt = jwt.encode(
            {
                "token": self.access_token_raw,
                "user_id": self.user_id,
                "type": "access",
                "exp": self.access_expiration.timestamp(),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        self.refresh_token_jwt = jwt.encode(
            {
                "token": self.refresh_token_raw,
                "user_id": self.user_id,
                "type": "refresh",
                "exp": self.refresh_expiration.timestamp(),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @property
    def is_access_expired(self):
        """Check if access token is expired"""
        return get_date() > self.access_expiration

    @property
    def is_refresh_expired(self):
        """Check if refresh token is expired"""
        return get_date() > self.refresh_expiration

    @property
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_access_expired

    def get_access_jwt(self):
        """Generate JWT for access token"""
        try:
            return jwt.encode(
                {
                    "token": self.access_token,
                    "user_id": self.user_id,
                    "exp": self.access_expiration.timestamp(),
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

    def decode_access_token(self, jwt_token=None):
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
        if jwt_token is None:
            jwt_token = self.get_access_jwt()

        return jwt.decode(
            jwt_token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )

    def decode_refresh_token(self, jwt_token=None):
        """Decode refresh token JWT"""
        if jwt_token is None:
            jwt_token = self.get_refresh_jwt()

        return jwt.decode(
            jwt_token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )

    def refresh_access_token(self, new_expiration):
        """Generate new access token"""

        if self.is_refresh_expired:
            raise ValueError("Refresh token is expired")

        self.access_token = secrets.token_urlsafe(64)
        self.access_expiration = new_expiration

        return self

    def revoke(self):
        """Revoke the token by setting expiration to past"""
        past_time = get_date().replace(year=2000)
        self.access_expiration = past_time
        self.refresh_expiration = past_time
        return self

    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens from database"""
        now = get_date()
        expired_tokens = cls.query.filter(
            db.and_(cls.access_expiration < now, cls.refresh_expiration < now)
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        db.session.commit()
        return count

    @classmethod
    def find_by_access_token(cls, access_token):
        """Find token by access token value"""
        return cls.query.filter_by(access_token=access_token).first()

    @classmethod
    def find_by_refresh_token(cls, refresh_token):
        """Find token by refresh token value"""
        return cls.query.filter_by(refresh_token=refresh_token).first()

    def get_allowed_update_fields(self):
        """Only allow updating expiration times"""
        return {"access_expiration", "refresh_expiration"}

    def validate_update(self, updates):
        """Validate token updates"""
        now = get_date()

        if "access_expiration" in updates:
            if updates["access_expiration"] <= now:
                raise ValueError("Access expiration must be in the future")

        if "refresh_expiration" in updates:
            if updates["refresh_expiration"] <= now:
                raise ValueError("Refresh expiration must be in the future")
