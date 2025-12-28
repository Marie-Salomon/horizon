from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_espacial'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    job = db.Column(db.String(100))
    password = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    user = request.form.get('username')
    fname = request.form.get('firstname')
    lname = request.form.get('lastname')
    job = request.form.get('job')
    pwd = request.form.get('password')
    
    if User.query.filter_by(username=user).first():
        flash("Cet identifiant est déjà utilisé.", "error")
        return redirect(url_for('signup_page'))

    hashed_pwd = generate_password_hash(pwd, method='pbkdf2:sha256')
    new_user = User(username=user, firstname=fname, lastname=lname, job=job, password=hashed_pwd)
    
    db.session.add(new_user)
    db.session.commit()
    
    session['user'] = user # Connexion auto
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')
    found_user = User.query.filter_by(username=user).first()
    
    if found_user and check_password_hash(found_user.password, pwd):
        session['user'] = user
        return redirect(url_for('dashboard'))
    
    flash("Identifiants incorrects.", "error")
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('home'))
    user_data = User.query.filter_by(username=session['user']).first()
    return render_template('dashboard.html', user=user_data)

@app.route('/journal/big-bang')
def big_bang():
    if 'user' not in session: return redirect(url_for('home'))
    return render_template('article_big_bang.html')

@app.route('/journal/black-holes')
def black_holes():
    if 'user' not in session: return redirect(url_for('home'))
    return render_template('article_black_holes.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)