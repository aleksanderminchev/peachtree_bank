from utils.utils import get_date
from app import db
from models.basemodel import BaseModel


class Contractor(BaseModel):

    __tablename__ = "contractors"

    # general
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)

    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    @staticmethod
    def find_by_name(name):
        return Contractor.query.filter(Contractor.name == f"%{name}%").first()