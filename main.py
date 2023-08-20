from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import request

from forms import ItineraryForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database for simplicity
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    itineraries = db.relationship('Itinerary', backref='user', lazy=True)


class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Step 5: Create Routes

@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Store username in session
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')



# ...

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if user:
        itineraries = user.itineraries  # Fetch user-specific itineraries

        if request.method == 'POST':
            form = ItineraryForm()

            if form.validate_on_submit():
                day = form.day.data
                location = form.location.data
                description = form.description.data

                new_itinerary = Itinerary(day=day, location=location, description=description, user=user)
                db.session.add(new_itinerary)
                db.session.commit()

                flash('Itinerary added successfully!', 'success')
                return redirect(url_for('dashboard'))
        else:
            form = ItineraryForm()

        return render_template('dashboard.html', username=username, itineraries=itineraries, form=form)
    else:
        flash('You need to be logged in to access the dashboard.', 'warning')
        return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
