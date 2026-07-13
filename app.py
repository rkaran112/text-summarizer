import os

from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

def summarizer(user_input):
    api_token = os.environ.get("HF_API_TOKEN")
    if not api_token:
        return "Error: HF_API_TOKEN environment variable is not set."

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {"inputs": user_input}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # If the request fails, it will raise an error
        return response.json()[0]["summary_text"]
    except requests.exceptions.Timeout:
        print("Error: Hugging Face API request timed out")
        return "Error: The request timed out. Please try again later."
    except requests.exceptions.HTTPError:
        if response.status_code == 503:
            wait_time = None
            try:
                wait_time = response.json().get("estimated_time")
            except ValueError:
                pass
            if wait_time:
                return f"The summarization model is still loading. Please try again in about {int(wait_time)} seconds."
            return "The summarization model is still loading. Please try again shortly."
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                return f"Rate limit reached. Please try again in about {retry_after} seconds."
            return "Rate limit reached. Please try again shortly."
        print(f"Error: {response.status_code} {response.text}")
        return "Error summarizing text. Please try again later."
    except Exception as e:
        print(f"Error: {e}")
        return "Error summarizing text. Please try again later."

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML form

@app.route('/process', methods=['POST'])
def process_text():
    user_input = request.form.get('user_input', '').strip()  # Get input text from the form
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    summarized_text = summarizer(user_input)
    return jsonify({"summary": summarized_text})

if __name__ == "__main__":
    app.run(debug=True)
