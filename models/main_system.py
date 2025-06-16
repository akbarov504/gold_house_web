import pytz
from models import db
from datetime import datetime, timezone

class MainSystem(db.Model):
    __tablename__ = 'main_system'

    id = db.Column(db.Integer(), primary_key=True)

    lom = db.Column(db.Float(), nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, lom, comment=None):
        super().__init__()
        self.lom = lom
        self.comment = comment
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
