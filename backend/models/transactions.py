import enum
from flask import abort
from sqlalchemy.orm import validates

from app import db
from utils.utils import get_date
from models.enums import CurrencyEnum, TransactionStatus, MethodEnum
from models.basemodel import BaseModel


class Transaction(BaseModel):  # type:ignore
    """
    Model for transactions
    """

    __tablename__ = "transactions"
    uid = db.Column(db.Integer, primary_key=True)
    hashed_id = db.Column(db.String(256), nullable=False)
    status = db.Column(
        db.Enum(TransactionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=TransactionStatus.SENT.value,
        server_default=TransactionStatus.SENT.value,
        index=True,
    )
    sent_at = db.Column(db.DateTime, nullable=True, index=True)
    payed_at = db.Column(db.DateTime, nullable=True, index=True)
    received_at = db.Column(db.DateTime, nullable=False, index=True)

    currency = db.Column(
        db.Enum(CurrencyEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=CurrencyEnum.USD.value,
        server_default=CurrencyEnum.USD.value,
    )
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(
        db.Enum(MethodEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=MethodEnum.TRANSACTION.value,
        server_default=MethodEnum.TRANSACTION.value,
        index=True,
    )
    # This is the payment intent ID
    tracking_id = db.Column(db.String(256), nullable=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractors.uid"), index=True)
    # One Contractor to Many transactions relation
    contractor = db.relationship("Contractor", backref="transactions")

    @staticmethod
    def get_transaction_by_id(id):
        return Transaction.query.get(id)
