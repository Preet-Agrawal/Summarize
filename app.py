import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Authenticate with the GitHub Copilot Models API
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.environ["GITHUB_TOKEN"],
)

def generate_openai_response(prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that creates structured summaries and quizzes.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="openai/gpt-4o-mini", 
        temperature=1,
        max_tokens=4096,
        top_p=1
    )
    return response.choices[0].message.content

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
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
    try:
        result = generate_openai_response(prompt)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=7000)
