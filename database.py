import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

def init_db(app):
    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)
    
    # Create database tables within app context
    with app.app_context():
        import models
        db.create_all()
        
        # Create default user if not exists
        from models import User
        from werkzeug.security import generate_password_hash
        
        if not User.query.first():
            default_user = User(password_hash=generate_password_hash("1234"))
            db.session.add(default_user)
            db.session.commit()