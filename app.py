import os
from flask import Flask, render_template, request
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
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="openai/gpt-4o-mini",  # or "openai/gpt-4o", "openai/gpt-4.1", etc.
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
        return "No input received.", 400

    prompt = f"""Summarize the following story and generate 3 multiple choice questions with 4 options each. Mark the correct answer with (✔️).

Story:
{user_text}
"""
    try:
        result = generate_openai_response(prompt)
        return result
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=7000)
