import pytz
from models import db
from datetime import datetime, timezone

class ClientDebt(db.Model):
    __tablename__ = 'client_debt'

    id = db.Column(db.Integer(), primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    lom = db.Column(db.Float(), nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, user_id, lom, comment=None):
        super().__init__()
        self.user_id = user_id
        self.lom = lom
        self.comment = comment
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
