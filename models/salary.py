from models import db
from datetime import datetime

class Salary(db.Model):
    __tablename__ = 'salary'

    id = db.Column(db.Integer(), primary_key=True)

    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float(), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, type, amount):
        super().__init__()
        self.type = type
        self.amount = amount
        self.created_at = datetime.now()
