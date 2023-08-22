#        Bishoy Sedrak - Sedrakb1     #
#        CSIT537_51SU23 - M8: Project 3 #

# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import request
from forms import ItineraryForm

# Create a Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Planner'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define User model representing the users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    itineraries = db.relationship('Itinerary', backref='user', lazy=True)

# Define Itinerary model representing the itineraries table
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Define route to display index page
@app.route('/')
def index():
    return render_template('layout.html')

# Define route to display shared itinerary
@app.route('/shared_itinerary/<int:id>')
def shared_itinerary(id):
    itinerary = Itinerary.query.get(id)
    return render_template('share_itinerary.html', itinerary=itinerary)

# Define route for user registration
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


# Define route for user login
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



# Define route for user dashboard
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

# Define route to delete an itinerary
@app.route('/delete_itinerary/<int:id>', methods=['GET', 'POST'])
def delete_itinerary(id):
    itinerary = Itinerary.query.get(id)
    if itinerary:
        db.session.delete(itinerary)
        db.session.commit() # Commit changes to the database
        flash('Itinerary deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# Define route to update an itinerary
@app.route('/update_itinerary', methods=['POST'])
def update_itinerary():
    if request.method == 'POST':
        itinerary_id = request.form.get('itinerary_id')
        updated_itinerary = Itinerary.query.get(itinerary_id)

        if updated_itinerary:
            # Update itinerary details
            updated_itinerary.day = request.form.get('day')
            updated_itinerary.location = request.form.get('location')
            updated_itinerary.description = request.form.get('description')

            db.session.commit() # Commit changes to the database
            flash('Itinerary updated successfully!', 'success')

    return redirect(url_for('dashboard'))

# Run the Flask app only if the script is executed directly
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)

#End of Code - Bishoy Sedrak