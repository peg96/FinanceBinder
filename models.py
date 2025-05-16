import datetime
from database import db

class Binder(db.Model):
    __tablename__ = 'binders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    categories = db.relationship('Category', backref='binder', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='binder', cascade='all, delete-orphan')

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default='#f8a5c2')  # Pastel pink
    binder_id = db.Column(db.Integer, db.ForeignKey('binders.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='category', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('name', 'binder_id', name='unique_category_per_binder'),
    )

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    binder_id = db.Column(db.Integer, db.ForeignKey('binders.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)