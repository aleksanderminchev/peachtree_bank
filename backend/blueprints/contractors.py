from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from apifairy import authenticate, body, response, other_responses
from sqlalchemy.orm import joinedload
from app import db
from models.contractors import Contractor
from schema.contractors import ContractorSchema

contractors = Blueprint("contractors", __name__)


@contractors.route("/get_contractors", methods=["GET"])
def get_contractors():
    schema = ContractorSchema(many=True)
    return schema.dump(Contractor.query.all())
