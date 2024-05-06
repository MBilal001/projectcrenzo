from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from model.database import *
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from io import BytesIO
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

 

app = Flask(__name__)
#Creating sessions for each.
app.secret_key = secrets.token_hex(16)

# Configure upload folder
app.config["UPLOAD_FOLDER"] = "uploads"
 
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_PERMANENT"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registration.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "ceoblz03@gmail.com" 
EMAIL_PASSWORD = "iyme rjlk pxbe cjtv"
  
def send_email_to_user(email, message):
    subject = "Rental Confirmation"

    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject

    # Add the message to the email body
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email, msg.as_string())


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name= request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user is registered
        user = Registrations.query.filter_by(email=email).first()

        if user:
            # User exists, check password
            if password == user.password:
                # Password correct, store email in session
                session["email"] = email
                session["name"] = name
                # Redirect to main page
                return redirect("/home")
            else:
                # Password incorrect, show login page again
                return render_template("login.html")
        else:
            # User does not exist, redirect to register page
            return redirect("/signup")

    # If GET request, simply render the login page
    return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")

        # Check if the email is already registered
        existing_user = Registrations.query.filter_by(email=email).first()

        if existing_user:
            # User already exists, redirect to login page
            return redirect("/login")

        # Create a new user
        new_user = Registrations(email=email, name=name, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Store email in session upon successful registration
        session["email"] = email
        session["name"] = name

        # Redirect to profile page after registration
        return redirect("/home")

    # If GET request, simply render the register page
    return render_template("signup.html")

@app.route("/logout")
def logout():
    # Clear the user session and redirect to the login page
    session.clear()
    return redirect("/")

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/vehicle')
def vehicle():
    return render_template('vehicle.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route("/image/<email>")
def get_image(email):
    user_image = UserProfileImage.query.filter_by(email=email).first()
    if user_image:
        image_extension = user_image.image_extension
        return Response(user_image.image_data, mimetype=image_extension)
    else:
        return send_file("default_profile_image.jpg", mimetype="image/jpeg")

@app.route("/profile", methods=["GET", "POST"])
def account():
    # Check if user is logged in
    if "email" in session:
        # Retrieve user data from session
        email = session["email"]
        # Query database for user details
        user = Registrations.query.filter_by(email=email).first()
        if user:
            name = user.name
            user_image = None  # Initialize user_image

            if request.method == "POST":
                # Retrieve form data

                if "file" in request.files:
                    file = request.files["file"]
                    if file.filename != "":
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        file.save(file_path)

                        with open(file_path, "rb") as f:
                            image_data = f.read()

                        _, image_extension = os.path.splitext(filename)

                        # Check if user image already exists
                        user_image = UserProfileImage.query.filter_by(
                            email=email
                        ).first()
                        if user_image:
                            # Update existing user image
                            user_image.image_data = image_data
                            user_image.image_extension = image_extension
                            user_image.image_filename = filename
                        else:
                            # Insert new user image
                            user_image = UserProfileImage(
                                email=email,
                                image_data=image_data,
                                image_extension=image_extension,
                                image_filename=filename,
                            )
                            db.session.add(user_image)
                        #commit to the database.
                        db.session.commit()

                return redirect("/profile")

            # Render profile template with user details and optional settings
            return render_template(
                "account.html",
                email=user.email,
                password=user.password,
                name=name,
                user_image=user_image,
            )
        else:
            name = "Unknown"
            # Handle case where user data is not found
            return "User data not found"
    else:
        # Redirect to login page if user is not logged in
        return redirect("/")
    
@app.route('/confirm')
def confirm():
    # Retrieve the user's email from the session
    user_email = session.get("email")
    if not user_email:
        # Handle the case where the email is not found in the session
        return "Email not found in session", 400

    # Send confirmation email to the user's email with a message
    message = "Thank you for choosing Crenzo. We are pleased to confirm your reservation and look forward to providing you with a seamless and enjoyable car rental experience"
    send_email_to_user(user_email, message)

    # Return a response, such as rendering a confirmation template
    return render_template('confirm.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        phone = request.form.get("phone")
        text = request.form.get("text")

        # Create a new commit
        new_message = Contact(name=name, email=email, phone=phone, text=text)
        db.session.add(new_message)
        db.session.commit()

        # Flash message to indicate successful submission
        flash('Form submitted successfully!', 'success')


    # Render the contact form template for GET requests
    return render_template('contact.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)