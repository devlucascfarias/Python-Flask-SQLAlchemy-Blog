from database import db
from datetime import datetime

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(500), nullable=False)
    cover_image_url = db.Column(db.String(500))  
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all,delete")
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(500), nullable=False)
    user_image = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    user_image = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)