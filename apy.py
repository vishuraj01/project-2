from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from wtforms.validators import Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'intheheaven',
    'database': 'project',
    'auth_plugin': 'mysql_native_password'  # Use 'caching_sha2_password' if needed
}

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view

# Create a connection to the database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Define your User table creation query
create_user_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(60) NOT NULL,
    email VARCHAR(255) DEFAULT ''  -- Add a default value for email
)
"""

# Execute the query to create the User table
cursor.execute(create_user_table_query)

# Commit the changes to the database
connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()

# Mock user database for demonstration purposes
class User(UserMixin):
    def __init__(self, user_id, username, password, email):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email


users = {1: User(1, 'user1', 'password1', 'user1@example.com'),
         2: User(2, 'user2', 'password2', 'user2@example.com')}


@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])  # Add this line
    submit = SubmitField('Register')

    def validate_username(self, field):
        if field.data.lower() in [u.username.lower() for u in users.values()]:
            raise ValidationError('Username is already taken.')

        # Query the database to check if the username already exists
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (field.data,))

        if cursor.fetchone():
            cursor.close()
            connection.close()
            raise ValidationError('Username is already taken.')

        cursor.close()
        connection.close()

@app.route('/')
def home():
    return render_template('home.html')

# app.py

# ... (previous code)

@app.route('/about')
def about():
    return render_template('about.html')

# ... (remaining code)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = next((u for u in users.values() if u.username == username and u.password == password), None)

        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
          # Establish a new connection and cursor
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        user_id = max(users.keys()) + 1
        username = form.username.data
        password = form.password.data
        email = form.email.data

        new_user = User(user_id, username, password, email)
        users[user_id] = new_user

        # Insert the new user into the database
        insert_user_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        user_data = (username, password, email)

        cursor.execute(insert_user_query, user_data)
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
