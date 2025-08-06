import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from forms import LoginForm
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_pymongo import PyMongo
from forms import RegistrationForm
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from flask_mail import Mail, Message

load_dotenv()
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
bcrypt = Bcrypt(app)

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Demo user store (replace with DB in production)
# Remove the users = {...} dictionary
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)


# To register a user (example)
if not mongo.db.users.find_one({"username": "testuser"}):
    hashed_pw = bcrypt.generate_password_hash("testpass").decode('utf-8')
    mongo.db.users.insert_one({"username": "testuser", "password": hashed_pw})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Hugging Face API (completely free)
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"

def generate_free_response(prompt):
    """Generate response using Hugging Face's free API"""
    try:
        # Use Hugging Face Inference API for text generation
        headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', '')}",
            "Content-Type": "application/json"
        }
        
        # Create a prompt for the AI to generate summary and quiz
        ai_prompt = f"""Please analyze this story and create a summary and 5 multiple choice questions.

Story: {prompt}

Please format your response exactly as follows:

SUMMARY:
[Write a concise summary of the story]

QUIZ:
1. [Question 1]
   A) [Option A]
   B) [Option B] 
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

2. [Question 2]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

3. [Question 3]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

4. [Question 4]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

5. [Question 5]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]
"""

        # Try Hugging Face API first
        if os.environ.get('HUGGINGFACE_API_KEY'):
            try:
                response = requests.post(
                    HUGGINGFACE_API_URL,
                    headers=headers,
                    json={"inputs": ai_prompt, "parameters": {"max_length": 1000, "temperature": 0.7}}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        return result.get('generated_text', '')
            except Exception as e:
                print(f"Hugging Face API error: {e}")
        
        # Fallback: Use a simple template if API fails or no key
        words = prompt.split()
        if len(words) > 50:
            summary = f"Summary of the story:\n{' '.join(words[:100])}...\n\nThis story appears to be about {words[0:5]} and contains various themes and characters."
        else:
            summary = f"Summary of the story:\n{prompt}\n\nThis is a brief story that can be analyzed for its key elements."
        
        quiz = """
QUIZ:
1. What type of content is this story?
   A) Fiction
   B) Non-fiction
   C) Poetry
   D) Technical
   Correct: A

2. What is the primary focus of this story?
   A) Characters
   B) Plot
   C) Setting
   D) Theme
   Correct: B

3. How would you describe the story's tone?
   A) Serious
   B) Humorous
   C) Mysterious
   D) Educational
   Correct: A

4. What is the most likely audience for this story?
   A) Children
   B) Adults
   C) Students
   D) Professionals
   Correct: C

5. What is the main lesson or message?
   A) Learning
   B) Adventure
   C) Friendship
   D) Success
   Correct: A
"""
        
        return f"SUMMARY:\n{summary}\n\n{quiz}"
        
    except Exception as e:
        return f"Error generating response: {str(e)}"



@app.route("/users")
@login_required
def list_users():
    users = list(mongo.db.users.find({}, {"_id": 0, "username": 1}))
    return render_template('users.html', users=users)


@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Flask app is working!"})

@app.route("/test_auth")
@login_required
def test_auth():
    return jsonify({"status": "ok", "message": "Authentication working!", "username": session.get('username')})

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/auth")
def auth_choice():
    return render_template('auth_choice.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists. Please choose another.', 'danger')
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            mongo.db.users.insert_one({"username": username, "password": hashed_pw})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = mongo.db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user["password"], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('hello_world'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('hello_world'))

@app.route("/profile")
@login_required
def profile():
    user = mongo.db.users.find_one({"username": session['username']}, {"_id": 0, "username": 1})
    quiz_results = list(mongo.db.quiz_results.find({"username": session['username']}))
    
    # Convert ObjectId to string for each quiz result
    for result in quiz_results:
        result['_id'] = str(result['_id'])
    
    return render_template('profile.html', user=user, quiz_results=quiz_results)


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        user_text = data.get("text", "")

        if not user_text:
            return jsonify({"error": "No input received."}), 400

        prompt = f"""Summarize the following story and generate 5 multiple choice questions with 4 options each. Format your response as follows:

SUMMARY:
[Write a concise summary of the story]

QUIZ:
1. [Question 1]
   A) [Option A]
   B) [Option B] 
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

2. [Question 2]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

3. [Question 3]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

4. [Question 4]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

5. [Question 5]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct: [A/B/C/D]

Story:
{user_text}
"""
        result = generate_free_response(prompt)
        # Save quiz generation to MongoDB for the logged-in user
        quiz_result = mongo.db.quiz_results.insert_one({
            "username": session['username'],
            "summary": result,  # This is the generated summary+quiz
            "score": None,      # You can update this later if you add scoring
            "date": datetime.utcnow()
        })
        return jsonify({"result": result, "quiz_id": str(quiz_result.inserted_id)})
    except Exception as e:
        print(f"Error in generate route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/save_score", methods=["POST"])
@login_required
def save_score():
    data = request.get_json()
    score = data.get("score")
    quiz_id = data.get("quiz_id")
    
    if score is None or quiz_id is None:
        return jsonify({"error": "Missing score or quiz_id"}), 400
    
    try:
        # Convert string ID back to ObjectId
        object_id = ObjectId(quiz_id)
        
        # Update the quiz result with the score
        mongo.db.quiz_results.update_one(
            {"_id": object_id, "username": session['username']},
            {"$set": {"score": score}}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/contact_submit", methods=["POST"])
def contact_submit():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    # Store in MongoDB if you want to save contact messages
    if name and email and message:
        mongo.db.contact_messages.insert_one({
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "date": datetime.utcnow()
        })
        
        # Send email notification if email is configured
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                # Send email to admin
                admin_email = os.environ.get('ADMIN_EMAIL', app.config['MAIL_USERNAME'])
                msg = Message(
                    subject=f"New Contact Form Submission: {subject}",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[admin_email]
                )
                msg.html = f"""
                <h3>New Contact Form Submission</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
                <hr>
                <p><small>Submitted on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</small></p>
                """
                mail.send(msg)
                
                # Send confirmation email to user
                user_msg = Message(
                    subject="Thank you for contacting Story Quiz",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )
                user_msg.html = f"""
                <h3>Thank you for reaching out, {name}!</h3>
                <p>We have received your message and will get back to you soon.</p>
                <p><strong>Your message:</strong></p>
                <p>{message}</p>
                <hr>
                <p>Best regards,<br>Story Quiz Team</p>
                """
                mail.send(user_msg)
                
            except Exception as e:
                print(f"Email sending failed: {e}")
                # Don't show error to user, just log it
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
    else:
        flash('Please fill in all required fields.', 'error')
    
    return redirect(url_for('contact'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use environment port or default to 5000
    host = os.environ.get("HOST", "127.0.0.1")  # Default to localhost for local development
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    
    print(f"Starting Story Quiz application...")
    print(f"Running on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(debug=debug, host=host, port=port)
