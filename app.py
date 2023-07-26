from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from user_table import User, db
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from os import getenv
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app=app)
login_manager = LoginManager()
login_manager.init_app(app=app)

# Line below only required once, when creating DB.
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        user = User()
        user.email = request.form.get('email')
        is_user_exist = User.query.filter_by(email=user.email).first()

        if is_user_exist:
            flash('A user is registered with this email, login instead')
            return redirect(url_for('login'))

        user.name = request.form.get('name')
        user.password = generate_password_hash(request.form.get('password'))

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account is created successfully')
        return redirect(url_for('secrets', name=current_user.name))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('You have been logged in successfully')
                return redirect(url_for('secrets'))
        flash("Password/Email is wrong")
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', 'files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
