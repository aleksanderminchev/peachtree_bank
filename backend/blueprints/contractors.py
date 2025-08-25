from flask import Blueprint
from apifairy import authenticate
from models.contractors import Contractor
from schema.contractors import ContractorSchema
from auth import token_auth

contractors = Blueprint("contractors", __name__)


@contractors.route("/get_contractors", methods=["GET"])
@authenticate(token_auth)
def get_contractors():
    schema = ContractorSchema(many=True)
    return schema.dump(Contractor.query.all())
