import os
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)

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
    color = db.Column(db.String(20), default='#f8a5c2')  # Pastel pink default
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

# Create tables
with app.app_context():
    db.create_all()
    
    # Create default user if not exists
    if not User.query.first():
        default_user = User(password_hash=generate_password_hash("1234"))
        db.session.add(default_user)
        db.session.commit()

# Check if user is logged in
def is_logged_in():
    return session.get('logged_in', False)

# Login required decorator
def login_required(route_function):
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            flash('Effettua il login per accedere', 'danger')
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        
        user = User.query.first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            flash('Login effettuato con successo', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Password non valida', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    binders = Binder.query.all()
    return render_template('dashboard.html', binders=binders)

@app.route('/api/binder', methods=['POST'])
@login_required
def create_binder():
    binder_name = request.form.get('binder_name')
    
    if not binder_name:
        flash('Il nome del raccoglitore è obbligatorio', 'danger')
        return redirect(url_for('dashboard'))
    
    existing_binder = Binder.query.filter_by(name=binder_name).first()
    if existing_binder:
        flash('Esiste già un raccoglitore con questo nome', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create new binder
    new_binder = Binder(name=binder_name)
    db.session.add(new_binder)
    db.session.commit()
    
    flash(f'Raccoglitore "{binder_name}" creato con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/binder/<int:binder_id>/delete', methods=['POST'])
@login_required
def delete_binder(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    
    db.session.delete(binder)
    db.session.commit()
    
    flash(f'Raccoglitore "{binder.name}" eliminato con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/binder/<int:binder_id>/category', methods=['POST'])
@login_required
def create_category(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    
    category_name = request.form.get('category_name')
    category_color = request.form.get('category_color', '#f8a5c2')  # Pastel pink default
    
    if not category_name:
        flash('Il nome della categoria è obbligatorio', 'danger')
        return redirect(url_for('dashboard'))
    
    existing_category = Category.query.filter_by(binder_id=binder_id, name=category_name).first()
    if existing_category:
        flash('Esiste già una categoria con questo nome in questo raccoglitore', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create new category
    new_category = Category(name=category_name, color=category_color, binder_id=binder_id)
    db.session.add(new_category)
    db.session.commit()
    
    flash(f'Categoria "{category_name}" creata con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Categoria "{category.name}" eliminata con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/binder/<int:binder_id>/transaction', methods=['POST'])
@login_required
def add_transaction(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    
    category_id = request.form.get('category_id')
    description = request.form.get('description', '')
    amount = request.form.get('amount')
    date_str = request.form.get('date')
    
    if not category_id or not amount or not date_str:
        flash('Categoria, importo e data sono obbligatori', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        category = Category.query.get_or_404(int(category_id))
        amount = float(amount)
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Dati non validi per la transazione', 'danger')
        return redirect(url_for('dashboard'))
    
    # Create new transaction
    transaction = Transaction(
        date=date,
        description=description,
        amount=amount,
        binder_id=binder_id,
        category_id=category.id
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    flash('Transazione aggiunta con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transazione eliminata con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/transaction/<int:transaction_id>/edit', methods=['POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    category_id = request.form.get('category_id')
    description = request.form.get('description', '')
    amount = request.form.get('amount')
    date_str = request.form.get('date')
    
    if not category_id or not amount or not date_str:
        flash('Categoria, importo e data sono obbligatori', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        category = Category.query.get_or_404(int(category_id))
        amount = float(amount)
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Dati non validi per la transazione', 'danger')
        return redirect(url_for('dashboard'))
    
    # Update transaction
    transaction.category_id = category.id
    transaction.description = description
    transaction.amount = amount
    transaction.date = date
    
    db.session.commit()
    
    flash('Transazione aggiornata con successo', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/binder/<int:binder_id>/data')
@login_required
def get_binder_data(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    categories = Category.query.filter_by(binder_id=binder_id).all()
    transactions = Transaction.query.filter_by(binder_id=binder_id).all()
    
    # Format data for JSON response
    categories_data = {}
    for category in categories:
        categories_data[category.id] = {
            'name': category.name,
            'color': category.color
        }
    
    transactions_data = []
    for transaction in transactions:
        transactions_data.append({
            'id': transaction.id,
            'date': transaction.date.isoformat(),
            'category_id': transaction.category_id,
            'category_name': Category.query.get(transaction.category_id).name,
            'description': transaction.description,
            'amount': transaction.amount
        })
    
    return jsonify({
        'id': binder.id,
        'name': binder.name,
        'categories': categories_data,
        'transactions': transactions_data
    })

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Tutti i campi sono obbligatori', 'danger')
        return redirect(url_for('dashboard'))
    
    if new_password != confirm_password:
        flash('Le nuove password non corrispondono', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.first()
    
    if not user or not check_password_hash(user.password_hash, current_password):
        flash('Password attuale non corretta', 'danger')
        return redirect(url_for('dashboard'))
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password cambiata con successo', 'success')
    return redirect(url_for('dashboard'))