from models import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    gramm = db.Column(db.Float(), nullable=False)
    proba = db.Column(db.Float(), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Float(), nullable=True, default=0)
    price = db.Column(db.Float(), nullable=False)
    qr_code = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, title, gramm, proba, type, number, status, price, qr_code, size=None):
        super().__init__()
        self.title = title
        self.gramm = gramm
        self.proba = proba
        self.type = type
        self.number = number
        self.status = status
        self.price = price
        self.qr_code = qr_code
        self.size = size
        self.created_at = datetime.now()
