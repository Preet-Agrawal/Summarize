from flask import Flask, render_template, request
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyBYwi1oCcneIDSfUEBQa_sqTatLYd1iXVg") 
def generate_gemini_response(prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text

@app.route("/")
def hello_world():
    print("Root route accessed")
    return render_template('index.html')

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_text = data.get("text", "")

    if not user_text:
        return "No input received.", 400

    prompt = f"""Summarize the following story and generate 3 multiple choice questions with 4 options each. Mark the correct answer with (✔️).

Story:
{user_text}
"""
    try:
        result = generate_gemini_response(prompt)
        return result
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, port=7000)
