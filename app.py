import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from forms import LoginForm
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_pymongo import PyMongo
from forms import RegistrationForm
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from flask_mail import Mail, Message

load_dotenv()
app = Flask(__name__)
CORS(app)

# IST timezone helper
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

@app.template_filter('to_ist')
def to_ist_filter(dt):
    """Convert UTC datetime to IST for display"""
    if dt:
        # If datetime is naive (no timezone), assume it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Convert to IST
        ist_time = dt.astimezone(IST)
        return ist_time
    return dt

# Ensure SECRET_KEY is set in production
if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('SECRET_KEY'):
    raise ValueError("SECRET_KEY must be set in production environment")
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

# MongoDB Configuration
mongo_uri = os.environ.get("MONGO_URI")
mongo = None
mongo_connected = False

if not mongo_uri:
    raise ValueError("MONGO_URI must be set in environment variables. Please check your .env file.")


try:
    # Validate URI format before attempting connection
    if not mongo_uri.startswith(('mongodb://', 'mongodb+srv://')):
        raise ValueError("Invalid MongoDB URI format. Must start with 'mongodb://' or 'mongodb+srv://'")
    
    # Set the URI in Flask config
    app.config["MONGO_URI"] = mongo_uri
    
    # Initialize PyMongo
    mongo = PyMongo()
    mongo.init_app(app)
    
    # Ensure mongo object is properly initialized
    if mongo is None:
        raise Exception("PyMongo initialization returned None")
    
    if not hasattr(mongo, 'db'):
        raise Exception("PyMongo object missing 'db' attribute")
    
    # Test the connection
    result = mongo.db.command('ping')
    if result.get('ok') != 1:
        raise Exception("MongoDB ping failed")
    
    mongo_connected = True
    print("Database connected")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("Please verify:")
    print("1. Your .env file exists and contains MONGO_URI")
    print("2. MongoDB Atlas cluster is running")
    print("3. Network access is configured (0.0.0.0/0)")
    print("4. Database user has proper permissions")
    raise

# Only create test user in development and if MongoDB is connected
if os.environ.get('FLASK_ENV') != 'production' and mongo_connected:
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

# Add favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content response

# Hugging Face API configuration for better models
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"  # Better for summarization
HUGGINGFACE_QA_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"  # Better for Q&A generation

def generate_free_response(story_text):
    """Generate summary and quiz using Hugging Face's AI models"""
    try:
        api_key = os.environ.get('HUGGINGFACE_API_KEY', '')
        
        if not api_key:
            # If no API key, use a more intelligent fallback
            return generate_smart_fallback(story_text)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Generate summary using BART model
        summary = ""
        try:
            summary_response = requests.post(
                HUGGINGFACE_API_URL,
                headers=headers,
                json={
                    "inputs": story_text,
                    "parameters": {
                        "max_length": 150,
                        "min_length": 30,
                        "do_sample": False
                    }
                },
                timeout=30
            )
            
            if summary_response.status_code == 200:
                summary_result = summary_response.json()
                if isinstance(summary_result, list) and len(summary_result) > 0:
                    summary = summary_result[0].get('summary_text', '')
                elif isinstance(summary_result, dict):
                    summary = summary_result.get('summary_text', '')
        except Exception as e:
            print(f"Summary generation error: {e}")
        
        # Step 2: Generate quiz questions using FLAN-T5
        quiz_prompt = f"""Based on this story, create 5 multiple choice questions with 4 options each. 

Story: {story_text[:1500]}  # Limit story length for API

Generate questions that test comprehension of:
1. Main characters and their roles
2. Key plot events
3. Setting and time period
4. Central conflict or problem
5. Theme or moral of the story

Format each question with options A, B, C, D and indicate the correct answer."""
        
        quiz_questions = []
        try:
            quiz_response = requests.post(
                HUGGINGFACE_QA_URL,
                headers=headers,
                json={
                    "inputs": quiz_prompt,
                    "parameters": {
                        "max_length": 500,
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if quiz_response.status_code == 200:
                quiz_result = quiz_response.json()
                if isinstance(quiz_result, list) and len(quiz_result) > 0:
                    quiz_text = quiz_result[0].get('generated_text', '')
                elif isinstance(quiz_result, dict):
                    quiz_text = quiz_result.get('generated_text', '')
                
                # Parse the generated quiz text
                if quiz_text:
                    quiz_questions = parse_quiz_from_text(quiz_text, story_text)
        except Exception as e:
            print(f"Quiz generation error: {e}")
        
        # If we didn't get good results, use intelligent fallback
        if not summary or len(quiz_questions) < 5:
            return generate_smart_fallback(story_text)
        
        # Format the final response
        quiz_formatted = format_quiz_questions(quiz_questions)
        return f"SUMMARY:\n{summary}\n\n{quiz_formatted}"
        
    except Exception as e:
        print(f"Error in generate_free_response: {e}")
        return generate_smart_fallback(story_text)

def generate_smart_fallback(story_text):
    """Generate story-specific summary and quiz questions"""
    import random
    
    # Extract key information from the story
    sentences = [s.strip() for s in story_text.split('.') if s.strip()]
    words = story_text.split()
    lower_text = story_text.lower()
    
    # Create a contextual summary
    if len(sentences) >= 3:
        # Take key sentences: beginning, important middle, and end
        summary_parts = []
        summary_parts.append(sentences[0])
        
        # Find sentences with action verbs or important keywords
        action_words = ['went', 'found', 'discovered', 'met', 'saw', 'heard', 'felt', 'took', 'gave', 'made', 'came', 'left', 'arrived', 'decided', 'realized', 'learned']
        for i, sent in enumerate(sentences[1:-1], 1):
            if any(word in sent.lower() for word in action_words):
                summary_parts.append(sent)
                break
        
        if sentences[-1] not in summary_parts:
            summary_parts.append(sentences[-1])
        
        summary = ". ".join(summary_parts) + "."
    else:
        summary = story_text
    
    # Extract character names intelligently
    common_words = {'The', 'She', 'He', 'They', 'It', 'We', 'I', 'You', 'One', 'Once', 'This', 'That', 'There', 'These', 'Those', 'Throughout', 'In', 'At', 'On', 'By', 'For', 'With', 'But', 'And', 'Or', 'So', 'If', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'Which', 'Every', 'Some', 'Many', 'Few', 'All', 'Any', 'After', 'Before', 'During', 'While', 'Since', 'Until', 'Curious', 'Suddenly', 'Finally', 'Eventually', 'Meanwhile', 'However', 'Therefore', 'Furthermore', 'Moreover', 'Nevertheless', 'Nonetheless', 'Otherwise', 'Instead', 'Indeed', 'Perhaps', 'Maybe', 'Certainly', 'Definitely', 'Probably', 'Possibly', 'Usually', 'Often', 'Sometimes', 'Always', 'Never', 'Just', 'Only', 'Even', 'Still', 'Already', 'Also', 'Too', 'Either', 'Neither', 'Both', 'Each', 'Every', 'Another', 'Other', 'Such', 'Rather', 'Quite', 'Very', 'Really', 'Actually', 'Basically', 'Generally', 'Specifically', 'Particularly', 'Especially'}
    
    potential_names = []
    for word in words:
        cleaned = word.strip('.,!?;:"\'-')
        if cleaned and cleaned[0].isupper() and len(cleaned) > 2 and cleaned not in common_words:
            potential_names.append(cleaned)
    
    unique_names = list(dict.fromkeys(potential_names))[:10]  # Keep order, get up to 10 unique names
    
    # Extract locations/places
    location_indicators = ['in', 'at', 'to', 'from', 'near', 'beside', 'under', 'over', 'through', 'across', 'into', 'onto']
    locations = []
    words_lower = [w.lower() for w in words]
    for i, word in enumerate(words_lower):
        if word in location_indicators and i + 1 < len(words):
            next_word = words[i + 1].strip('.,!?;:')
            if next_word and next_word[0].isupper():
                locations.append(next_word)
    
    # Extract key objects/things mentioned
    objects = []
    object_patterns = ['a', 'an', 'the']
    for i, word in enumerate(words_lower):
        if word in object_patterns and i + 1 < len(words):
            next_word = words[i + 1].strip('.,!?;:')
            if next_word and not next_word[0].isupper() and len(next_word) > 3:
                objects.append(next_word.lower())
    unique_objects = list(dict.fromkeys(objects))[:10]
    
    # Detect story elements
    has_dialogue = '"' in story_text or "'" in story_text or 'said' in lower_text or 'asked' in lower_text or 'replied' in lower_text
    
    # Detect time references
    time_words = ['morning', 'afternoon', 'evening', 'night', 'day', 'week', 'month', 'year', 'yesterday', 'today', 'tomorrow', 'once', 'then', 'now', 'later', 'before', 'after']
    time_references = [word for word in time_words if word in lower_text]
    
    # Detect emotions/feelings
    emotion_words = ['happy', 'sad', 'angry', 'scared', 'excited', 'worried', 'surprised', 'confused', 'proud', 'disappointed', 'loved', 'hated', 'feared', 'hoped', 'wished']
    emotions_found = [word for word in emotion_words if word in lower_text]
    
    # Generate dynamic quiz questions based on the story content
    quiz = "QUIZ:\n"
    questions = []
    
    # Question pool based on what we found in the story
    
    # Character-based questions
    if len(unique_names) >= 2:
        main_char = unique_names[0]
        other_chars = unique_names[1:4] if len(unique_names) > 1 else ['nobody', 'someone', 'a stranger']
        questions.append({
            'q': f"Who is the main character in this story?",
            'options': [main_char, other_chars[0] if len(other_chars) > 0 else 'John', 
                       other_chars[1] if len(other_chars) > 1 else 'Mary', 
                       'The narrator'],
            'correct': 'A'
        })
        
        if len(unique_names) >= 3:
            questions.append({
                'q': f"Which character appears after {unique_names[0]} in the story?",
                'options': [unique_names[1], unique_names[2] if len(unique_names) > 2 else 'Nobody',
                           unique_names[0], 'An unnamed character'],
                'correct': 'A'
            })
    
    # Location-based questions
    if locations:
        questions.append({
            'q': "Where does part of this story take place?",
            'options': [locations[0], 'In a city', 'In space', 'Underwater'],
            'correct': 'A'
        })
    
    # Object-based questions
    if unique_objects:
        questions.append({
            'q': f"What object is mentioned in the story?",
            'options': [unique_objects[0], 'a sword', 'a map', 'a key'],
            'correct': 'A'
        })
    
    # Plot-based questions
    action_verbs_in_story = []
    action_check = ['found', 'discovered', 'met', 'saw', 'went', 'came', 'took', 'gave', 'made', 'ran', 'jumped', 'flew', 'fell', 'climbed', 'opened', 'closed', 'broke', 'fixed', 'helped', 'saved', 'fought', 'won', 'lost', 'died', 'lived', 'grew', 'changed', 'became', 'turned', 'returned']
    for verb in action_check:
        if verb in lower_text:
            action_verbs_in_story.append(verb)
    
    if action_verbs_in_story:
        questions.append({
            'q': f"What action occurs in the story?",
            'options': [f"Someone {action_verbs_in_story[0]}", 'Someone sleeps', 'Someone dances', 'Someone sings'],
            'correct': 'A'
        })
    
    # Time-based questions
    if time_references:
        questions.append({
            'q': "When does this story take place?",
            'options': [f"During the {time_references[0]}", 'In the future', 'In ancient times', 'Time is not specified'],
            'correct': 'A'
        })
    
    # Emotion-based questions
    if emotions_found:
        questions.append({
            'q': "What emotion is expressed in the story?",
            'options': [emotions_found[0].capitalize(), 'Boredom', 'Jealousy', 'No emotions mentioned'],
            'correct': 'A'
        })
    
    # Story structure questions
    questions.append({
        'q': "How does the story begin?",
        'options': [sentences[0][:50] + "..." if len(sentences[0]) > 50 else sentences[0],
                   "With a battle scene", "With a description of the weather", "With dialogue"],
        'correct': 'A'
    })
    
    if len(sentences) > 1:
        questions.append({
            'q': "How does the story end?",
            'options': [sentences[-1][:50] + "..." if len(sentences[-1]) > 50 else sentences[-1],
                       "With everyone living happily ever after", "With a cliffhanger", "With a moral lesson"],
            'correct': 'A'
        })
    
    # Dialogue questions - make them more specific
    if has_dialogue:
        if '"' in story_text:
            questions.append({
                'q': "What do characters do in this story?",
                'options': ["They speak to each other", "They remain silent", "They only think", "They only write letters"],
                'correct': 'A'
            })
        elif 'said' in lower_text:
            questions.append({
                'q': "How do characters communicate?",
                'options': ["Someone said something", "Through telepathy", "Using sign language", "They don't communicate"],
                'correct': 'A'
            })
    
    # Theme questions based on content
    if 'learn' in lower_text or 'lesson' in lower_text or 'realize' in lower_text:
        questions.append({
            'q': "What type of story is this?",
            'options': ["A story with a lesson or moral", "A pure action story", "A romance", "A mystery"],
            'correct': 'A'
        })
    
    # Additional content-based questions
    
    # Check for specific story elements
    if 'but' in lower_text or 'however' in lower_text or 'although' in lower_text:
        questions.append({
            'q': "What kind of conflict or challenge appears in the story?",
            'options': ["A problem that needs to be overcome", "Everything goes smoothly", "No challenges mentioned", "Multiple unsolved problems"],
            'correct': 'A'
        })
    
    # Look for descriptive words
    descriptive_words = ['beautiful', 'ugly', 'big', 'small', 'tall', 'short', 'dark', 'bright', 'mysterious', 'strange', 'magical', 'ordinary', 'special', 'dangerous', 'safe']
    found_descriptive = [word for word in descriptive_words if word in lower_text]
    if found_descriptive:
        questions.append({
            'q': f"How is something described in the story?",
            'options': [found_descriptive[0].capitalize(), "Boring", "Normal", "Not described"],
            'correct': 'A'
        })
    
    # Check for movement or travel
    travel_words = ['went', 'traveled', 'journeyed', 'walked', 'ran', 'flew', 'drove', 'sailed', 'arrived', 'departed', 'left', 'came']
    travel_found = [word for word in travel_words if word in lower_text]
    if travel_found:
        questions.append({
            'q': "What kind of movement happens in the story?",
            'options': [f"Someone {travel_found[0]}", "Everyone stays in one place", "Only thoughts move", "No movement occurs"],
            'correct': 'A'
        })
    
    # Randomly select 5 questions from our pool
    random.shuffle(questions)
    selected_questions = questions[:5]
    
    # If we don't have enough questions, create more specific content questions
    while len(selected_questions) < 5:
        backup_questions = []
        
        # Create questions about specific words in the story
        important_words = [w for w in words if len(w) > 5 and w[0].isupper()]
        if important_words and len(backup_questions) < 3:
            backup_questions.append({
                'q': f"Which word appears in the story?",
                'options': [important_words[0], "Elephant", "Computer", "Spaceship"],
                'correct': 'A'
            })
        
        # Question about what the story is NOT about
        if len(backup_questions) < 3:
            backup_questions.append({
                'q': "What is this story NOT about?",
                'options': ["Aliens from Mars", unique_names[0] if unique_names else "A character", 
                           unique_objects[0] if unique_objects else "An event", "The events described"],
                'correct': 'A'
            })
        
        # Question about story setting
        if len(backup_questions) < 3:
            if 'forest' in lower_text or 'tree' in lower_text:
                setting = "nature"
            elif 'city' in lower_text or 'building' in lower_text or 'street' in lower_text:
                setting = "urban area"
            elif 'house' in lower_text or 'home' in lower_text or 'room' in lower_text:
                setting = "indoor location"
            else:
                setting = "specific location"
                
            backup_questions.append({
                'q': "Where might this story take place?",
                'options': [f"In a {setting}", "On the moon", "Under the ocean", "In outer space"],
                'correct': 'A'
            })
        
        if backup_questions:
            selected_questions.append(backup_questions[0])
        else:
            # Last resort - ask about story purpose
            selected_questions.append({
                'q': "What is the purpose of this story?",
                'options': ["To tell a story", "To sell a product", "To provide instructions", "To list facts"],
                'correct': 'A'
            })
    
    # Format the selected questions with randomized answer positions
    for i, q_data in enumerate(selected_questions, 1):
        quiz += f"{i}. {q_data['q']}\n"
        
        # Get the options and randomize their order
        options = q_data['options'][:4]  # Ensure we have exactly 4 options
        while len(options) < 4:
            options.append("Not applicable")
        
        # Remember the correct answer before shuffling
        correct_answer = options[0]  # The first option is always the correct one in our data
        
        # Shuffle the options
        random.shuffle(options)
        
        # Find where the correct answer ended up
        correct_index = options.index(correct_answer)
        correct_letter = ['A', 'B', 'C', 'D'][correct_index]
        
        # Write the shuffled options
        for j, option in enumerate(['A', 'B', 'C', 'D']):
            quiz += f"   {option}) {options[j]}\n"
        quiz += f"   Correct: {correct_letter}\n\n"
    
    return f"SUMMARY:\n{summary}\n\n{quiz.rstrip()}"

def parse_quiz_from_text(quiz_text, story_text):
    """Parse quiz questions from generated text"""
    questions = []
    # This is a simplified parser - in production, you'd want more robust parsing
    lines = quiz_text.split('\n')
    current_question = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a question number
        if line[0].isdigit() and '.' in line[:3]:
            if current_question:
                questions.append(current_question)
            current_question = {'question': line, 'options': [], 'correct': 'A'}
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_question.get('options', []).append(line)
        elif 'correct' in line.lower() or 'answer' in line.lower():
            # Try to extract correct answer
            for char in ['A', 'B', 'C', 'D']:
                if char in line:
                    current_question['correct'] = char
                    break
    
    if current_question:
        questions.append(current_question)
    
    # Ensure we have 5 questions
    while len(questions) < 5:
        questions.append(create_generic_question(len(questions) + 1, story_text))
    
    return questions[:5]

def create_generic_question(num, story_text):
    """Create a generic question based on story analysis"""
    questions_bank = [
        {
            'question': f'{num}. What is the main theme of this story?',
            'options': [
                'A) Adventure and discovery',
                'B) Love and relationships',
                'C) Conflict and resolution',
                'D) Growth and learning'
            ],
            'correct': 'C'
        },
        {
            'question': f'{num}. What narrative technique is used in this story?',
            'options': [
                'A) Flashback',
                'B) Linear progression',
                'C) Multiple perspectives',
                'D) Stream of consciousness'
            ],
            'correct': 'B'
        },
        {
            'question': f'{num}. What is the story\'s primary conflict?',
            'options': [
                'A) Person vs. Person',
                'B) Person vs. Nature',
                'C) Person vs. Self',
                'D) Person vs. Society'
            ],
            'correct': 'A'
        }
    ]
    return questions_bank[num % len(questions_bank)] if num <= len(questions_bank) else questions_bank[0]

def format_quiz_questions(questions):
    """Format quiz questions for output"""
    quiz = "QUIZ:\n"
    for i, q in enumerate(questions, 1):
        quiz += f"{q.get('question', f'{i}. Question {i}')}\n"
        for opt in q.get('options', []):
            quiz += f"   {opt}\n"
        quiz += f"   Correct: {q.get('correct', 'A')}\n\n"
    return quiz.rstrip()



@app.route("/users")
@login_required
def list_users():
    if not mongo_connected:
        flash('Database unavailable. Please try again later.', 'error')
        return redirect(url_for('hello_world'))
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
    return render_template('index.html', mongo_connected=mongo_connected)

@app.route("/auth")
def auth_choice():
    return render_template('auth_choice.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check if username already exists
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists. Please choose another.', 'danger')
        else:
            # Create new user
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            mongo.db.users.insert_one({
                "username": username, 
                "password": hashed_pw,
                "created_at": get_ist_time()
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Find user in MongoDB
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

        # Pass the user's story text directly to the AI function
        result = generate_free_response(user_text)
        
        # Save quiz generation to MongoDB
        quiz_result = mongo.db.quiz_results.insert_one({
            "username": session['username'],
            "story": user_text,
            "summary": result,
            "score": None,
            "date": get_ist_time()
        })
        quiz_id = str(quiz_result.inserted_id)
        
        return jsonify({"result": result, "quiz_id": quiz_id})
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
    
    # Store in MongoDB
    if name and email and message:
        try:
            mongo.db.contact_messages.insert_one({
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "date": get_ist_time()
            })
        except Exception as e:
            print(f"Failed to save contact message to database: {e}")
        
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
                <p><small>Submitted on {get_ist_time().strftime('%Y-%m-%d %H:%M IST')}</small></p>
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

# Only run Flask dev server in development, not production
if __name__ == "__main__" and os.environ.get("FLASK_ENV") != "production":
    # Use PORT from environment (Render provides this), fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Listen on all interfaces
    debug = True
    
    print(f"Starting Story Quiz application in development mode...")
    print(f"Running on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(debug=debug, host=host, port=port)
