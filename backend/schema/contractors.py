from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.contractors import Contractor


class ContractorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contractor
        load_instance = True
