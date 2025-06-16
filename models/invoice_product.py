import pytz
from models import db
from datetime import datetime, timezone

class InvoiceProduct(db.Model):
    __tablename__ = 'invoice_product'

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(db.Integer(), db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, invoice_id, product_id):
        super().__init__()
        self.invoice_id = invoice_id
        self.product_id = product_id
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
