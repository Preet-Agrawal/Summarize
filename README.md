# Story Quiz - AI-Powered Story Summarizer & Quiz Generator

An interactive web application that uses AI to summarize stories and automatically generate quizzes to test comprehension. Built with Flask, MongoDB, and AI APIs, this project helps students improve their reading comprehension through engaging, interactive quizzes.

## Features
- 📚 **AI-Powered Summarization**: Automatically summarize long stories and texts
- 🎯 **Instant Quiz Generation**: Generate comprehension quizzes based on the story content
- 👤 **User Authentication**: Secure login and registration system
- 📊 **Progress Tracking**: Track quiz scores and performance history
- 📱 **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- 🎨 **Modern UI**: Clean, animated interface with gradient effects

## Quick Start (Local Development)

### Option 1: Using npm (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Summarize.git
cd Summarize

# Set up the project (installs dependencies and creates .env)
npm run setup

# Edit .env with your MongoDB URI and API keys
# Then start the application
npm start

# Open in browser
# Visit http://localhost:5000
```

### Option 2: Using Python directly

```bash
# Clone the repository
git clone https://github.com/yourusername/Summarize.git
cd Summarize

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your MongoDB URI and API keys

# Run the application
python app.py

# Open in browser
# Visit http://localhost:5000
```

## Prerequisites

Before running this project, make sure you have the following installed:

- **Python 3.7+**
- **MongoDB** (local or cloud instance like MongoDB Atlas)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Summarize.git
cd Summarize
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Then edit the `.env` file with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
HOST=127.0.0.1  # Localhost for local development
PORT=5000

# MongoDB Configuration
# For local MongoDB:
MONGO_URI=mongodb://localhost:27017/storyquiz
# Or for MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/storyquiz

# Groq API Configuration (for AI features)
GROQ_API_KEY=your-groq-api-key-here

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Initialize MongoDB

Make sure MongoDB is running:

```bash
# For local MongoDB
mongod

# The app will automatically create the required database and collections
```

### 6. Run the Application

#### Using npm:
```bash
npm start
# or for development mode with debug
npm run dev
```

#### Using Python directly:
```bash
python app.py
```

You should see output like:
```
Starting Story Quiz application...
Running on http://127.0.0.1:5000
Debug mode: True
```

The application will be accessible at:
- **Local access**: `http://localhost:5000` or `http://127.0.0.1:5000`
- **Network access**: Use `HOST=0.0.0.0` in `.env` to allow network access

## Available npm Scripts

```bash
npm start           # Start the application
npm run dev         # Start in development mode with debug
npm run setup       # Install dependencies and create .env file
npm run mongo       # Start MongoDB locally
npm run install     # Install Python dependencies

# Platform-specific commands
npm run start:windows  # Start on Windows
npm run start:mac      # Start on macOS/Linux
npm run setup:windows  # Setup on Windows
```

## Project Structure

```
Summarize/
├── app.py                 # Main Flask application
├── forms.py              # WTForms for user authentication
├── requirements.txt      # Python dependencies
├── static/
│   ├── style.css        # Main stylesheet
│   ├── script.js        # JavaScript functionality
│   └── images/
│       └── logo.jpg     # Application logo
├── templates/
│   ├── index.html       # Home page
│   ├── contact.html     # Contact page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── profile.html     # User profile
│   ├── auth_choice.html # Authentication choice
│   └── users.html       # User list (admin)
└── README.md            # Project documentation
```

## Usage

1. **Register/Login**: Create a new account or login with existing credentials
2. **Submit a Story**: Paste your story text in the input area
3. **Generate Summary & Quiz**: Click "Summarize & Quiz" to process your story
4. **Take the Quiz**: Answer the generated questions to test comprehension
5. **View Results**: Check your score and review correct answers
6. **Track Progress**: Visit your profile to see quiz history and statistics

## API Keys

This project requires a Groq API key for AI functionality:

1. Sign up at [Groq Console](https://console.groq.com)
2. Generate an API key
3. Add it to your `.env` file

## Deployment

### Deploy to Render (Recommended)

#### Method 1: One-Click Deploy
1. Push your code to GitHub
2. Click "New +" → "Web Service" on [Render Dashboard](https://dashboard.render.com)
3. Connect your GitHub repository
4. Render will auto-detect the configuration from `render.yaml`
5. Set environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `GROQ_API_KEY`: Your Groq API key
6. Click "Create Web Service"

#### Method 2: Manual Configuration
1. Push to GitHub
2. On Render Dashboard:
   - **Build Command**: `npm run build`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3
3. Add environment variables in Settings
4. Deploy

#### Required Environment Variables for Render:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/storyquiz
GROQ_API_KEY=your-groq-api-key
# SECRET_KEY will be auto-generated
```

The app will be available at: `https://your-app-name.onrender.com`

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in project directory
3. Follow the prompts to deploy

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: Groq API (Llama model)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login, Werkzeug
- **Forms**: Flask-WTF
- **Styling**: Custom CSS with animations

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in `.env`
   - Verify network access for cloud databases

2. **API Key Error**
   - Verify Groq API key is valid
   - Check API key is properly set in `.env`

3. **Port Already in Use**
   - Change port in `app.py` or use `PORT` environment variable
   - Kill existing process using the port

4. **Module Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Team

- **Preet Kumar** - Full Stack Developer
- **Kalpana Singh** - Backend Developer

*A 3rd Year Project by IIIT Surat Students*

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please use the Contact page in the application or reach out to the team members.
