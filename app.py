from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
import random

# Load model and tokenizer (takes ~30 secs the first time)
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

# Set up Flask
app = Flask(__name__)
CORS(app)

# Normalizing greetings function (Step 1)
def normalize_greeting(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # remove non-letter characters
    # Fix stretched words like "hiiiiii", "helloooo"
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)  # "hiiiiii" -> "hii"
    return text

# Function to detect if the message is nonsense (length or character check)
def is_nonsense(text):
    return not any(word.isalpha() for word in text.split())

# Function to check if input is too long
def is_too_long(text):
    return len(text) > 20

# Function to detect playful or sarcastic text
def is_playful(text):
    playful_keywords = ["your dad", "haha", "lol", "joking", "sarcastic"]
    return any(keyword in text.lower() for keyword in playful_keywords)

# Function to check if it's a question
def is_question(text):
    return text.strip().endswith('?')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    # Normalize user input
    normalized_input = normalize_greeting(user_input)
    
    # Check if it's a greeting and return a custom response if it is
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "yo", "sup", "heyyo", "howdy"]
    if any(greet in normalized_input for greet in greetings):
        # Define greeting responses (you can make this list bigger)
        greetings_responses = [
            "Hi there! 😊", 
            "Hello! How can I help you today?", 
            "Hey! What's up?", 
            "Hello, friend!", 
            "Hey hey! How’s it going?", 
            "Hi! Ready to chat?"
        ]
        bot_reply = random.choice(greetings_responses)
    
    # Handle nonsense or unclear input
    elif is_nonsense(normalized_input):
        bot_reply = "Hmm, that seems a bit confusing. Can you try rephrasing?"
    
    # Handle overly long input
    elif is_too_long(normalized_input):
        bot_reply = "That's a lot of 'o's! Can you try something shorter?"
    
    # Handle playful or sarcastic input
    elif is_playful(normalized_input):
        bot_reply = "That's a nice one! 😄 What's up?"
    
    # Handle questions
    elif is_question(normalized_input):
        bot_reply = "Hmm, that's a good question! Let me think about it."
    
    else:
        # Encode user input and add end-of-string token for non-greeting responses
        inputs = tokenizer.encode(normalized_input + tokenizer.eos_token, return_tensors="pt")

        # Generate response using model
        response_ids = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        bot_reply = tokenizer.decode(response_ids[:, inputs.shape[-1]:][0], skip_special_tokens=True)

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
