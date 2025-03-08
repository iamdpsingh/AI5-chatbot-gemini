from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-latest")
chat = model.start_chat(history=[])

conversation_file = 'conversations.json'

def load_conversations():
    if os.path.exists(conversation_file):
        with open(conversation_file, 'r') as f:
            return json.load(f)
    return {}

def save_conversation(user_input, response):
    conversations = load_conversations()
    conversations[user_input] = response
    with open(conversation_file, 'w') as f:
        json.dump(conversations, f, indent=4)

def get_gemini_response(user_input):
    response = chat.send_message(user_input, stream=True)
    full_response = ""
    for chunk in response:
        full_response += chunk.text
    save_conversation(user_input, full_response)
    return full_response

@app.route('/HosBot')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get('message')
    conversations = load_conversations()

    if user_input in conversations:
        response = conversations[user_input]
    else:
        response = get_gemini_response(user_input)
        response = re.sub(r"\*", "", response)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
