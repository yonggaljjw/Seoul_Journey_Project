from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    query_text = db.Column(db.Text)
    merged_query = db.Column(db.Text)
    travel_type = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    budget = db.Column(db.Integer)
    result = db.Column(db.JSON)
    weather = db.Column(db.JSON)
    public_data_candidates = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)