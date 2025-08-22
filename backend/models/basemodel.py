from app import db
from utils.utils import get_date
from sqlalchemy.exc import SQLAlchemyError


class BaseModel(db.Model):
    """Abstract base class for all models with common CRUD operations"""

    __abstract__ = True  # This tells SQLAlchemy not to create a table for this class

    # Common fields that all models might have
    created_at = db.Column(db.DateTime, default=get_date)
    updated_at = db.Column(
        db.DateTime,
        default=get_date,
        onupdate=get_date,
    )

    def update(self, commit=True, **kwargs):
        """
        Generic update method that can be overridden

        Args:
            commit (bool): Whether to commit changes immediately
            **kwargs: Fields to update
        """

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        if commit:
            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e

        return self
