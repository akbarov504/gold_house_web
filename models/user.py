import pytz
from models import db, login_manager
from datetime import datetime, timezone
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)

    full_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    chat_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, full_name, username, phone_number, password, role):
        super().__init__()
        self.full_name = full_name
        self.username = username
        self.phone_number = phone_number
        self.chat_id = None
        self.password = password
        self.role = role
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
    
    def to_dict_from_api(self):
        dict_user = {
            "id": self.id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "username": self.username,
            "password": self.password
        }
        return dict_user
