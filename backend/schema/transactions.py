from app import ma

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.transactions import Transaction
from models.contractors import Contractor


class AddTransactionSchema(ma.Schema):
    currency = ma.String(required=False)
    contractor_id = ma.Integer(required=False)
    contractor_name = ma.String(required=True)
    amount = ma.Float(required=True)
    method = ma.String(required=False)
    tracking_id = ma.String(required=False)


class ContractorNestedSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contractor
        load_instance = True
        include_fk = True
        # only include id and name
        fields = ("uid", "name")


class TransactionSchema(SQLAlchemyAutoSchema):
    contractor = fields.Nested(ContractorNestedSchema)

    class Meta:
        model = Transaction
        load_instance = True
        include_fk = True
        include_relationships = True

    # explicitly define fields if you want full control
    uid = auto_field()
    status = auto_field()
    sent_at = auto_field()
    payed_at = auto_field()
    received_at = auto_field()
    currency = auto_field()
    amount = auto_field()
    method = auto_field()
    tracking_id = auto_field()
    contractor_id = auto_field()
