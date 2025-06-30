from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re
import random
from langdetect import detect
from googletrans import Translator

# Load model and tokenizer (takes ~30 secs the first time)
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

# Set up Flask
app = Flask(__name__)
CORS(app)

translator = Translator()

def translate_to_english(text):
    translated = translator.translate(text, src = 'auto', dest = 'en')
    return translated.text

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'
    
def preprocess_user_input(user_input):
    lang = detect_language(user_input)
    print(f"Detected language: {lang}")  # Debugging the language detection
    if lang != 'en':  # If the language is not English
        translated_input = translate_to_english(user_input)  # Translate Nepali to English
        print(f"Original: {user_input} | Translated: {translated_input}")
        return translated_input, lang
    return user_input, lang


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

faq_responses = {
    "what should i do when i feel anxious" : "Try to take deep breaths, find a calm space, and remind yourself it's okay to feel this way. You're not alone. 🌱",
    "how can i improve my mental health" : "Consider talking to someone you trust, practicing mindfulness, or seeking professional help. Remember, it's okay to ask for support. 💚",
    "what are some ways to cope with stress" : "Engage in activities you enjoy, exercise, or practice relaxation techniques. It's important to take care of yourself. 🌼",
    "how can i manage my time better" : "Try breaking tasks into smaller steps, setting priorities, and using tools like calendars or to-do lists. You've got this! 📅",
    "what should i do if i feel overwhelmed" : "Take a step back, breathe, and focus on one thing at a time. It's okay to take breaks and ask for help. 🌈",
    "how can i build better relationships" : "Communicate openly, listen actively, and show appreciation. Building connections takes time, but it's worth it! 🤝",
    "what are some good self-care practices" : "Make time for yourself, whether it's reading, taking a walk, or enjoying a hobby. Self-care is essential for your well-being. 🌟",
    "how can i stay motivated" : "Set small, achievable goals, celebrate your progress, and remember why you started. You've got the strength to keep going! 💪",
    "what should i do if i feel sad" : "It's okay to feel sad sometimes. Talk to someone you trust, write down your feelings, or engage in activities that bring you joy. 🌻",
    "how can i practice mindfulness" : "Start with simple breathing exercises, focus on the present moment, and try to let go of distractions. Mindfulness can help you feel more grounded. 🌸",
    "can i talk to you when i feel sad": "Of course you can. I’m here to listen whenever you need. 💙",
    "do you judge people": "Not at all. I’m just here to support you, no matter what you're going through.",
    "what if i don’t want to talk": "That’s totally okay. Take your time — I’ll be right here whenever you’re ready. 🕊️",
    "can you help me calm down": "Let’s try something together. Breathe in... hold for 4 seconds... and breathe out slowly. You’re doing great. 🌼"
}

# Keyword mapping to FAQ questions
faq_keywords = {
    "anxious": "what should i do when i feel anxious",
    "anxiety": "what should i do when i feel anxious",
    "sad": "what should i do if i feel sad",
    "depressed": "what should i do if i feel sad",
    "overwhelmed": "what should i do if i feel overwhelmed",
    "stress": "what are some ways to cope with stress",
    "motivated": "how can i stay motivated",
    "motivation": "how can i stay motivated",
    "mental health": "how can i improve my mental health",
    "focus": "how can i manage my time better",
    "time": "how can i manage my time better",
    "relationships": "how can i build better relationships",
    "self-care": "what are some good self-care practices",
    "mindfulness": "how can i practice mindfulness",
    "calm": "can you help me calm down",
    "talk": "can i talk to you when i feel sad"
}

last_bot_repsonse = ""

@app.route('/chat', methods=['POST'])
def chat():
    global last_bot_repsonse
    data = request.get_json()
    user_input = data.get("message")

    # Detect and translate if needed
    processed_input, lang = preprocess_user_input(user_input)
    normalized_input = normalize_greeting(processed_input).strip().lower()

    for keyword, faq_key in faq_keywords.items():
        if keyword in normalized_input:
            return jsonify({"reply": faq_responses[faq_key]})

    greetings = ["hi", "hello", "hey", "good morning", "good evening", "yo", "sup", "heyyo", "howdy"]
    if any(word in normalized_input.split() for word in greetings):
        bot_reply = random.choice([
            "Hi there! 😊", 
            "Hello! How can I help you today?", 
            "Hey! What's up?", 
            "Hello, friend!", 
            "Hey hey! How’s it going?", 
            "Hi! Ready to chat?"
        ])
    
    elif "how are you" in normalized_input:
        bot_reply = "I'm doing great, thanks for asking! How about you?"

    elif normalized_input in faq_responses:
        bot_reply = faq_responses[normalized_input]

    elif is_too_long(normalized_input) and normalized_input not in faq_responses:
        bot_reply = "That's a lot to unpack! Can you simplify it a bit?"

    elif is_nonsense(normalized_input):
        bot_reply = "Hmm, that seems a bit confusing. Can you try rephrasing?"

    elif is_too_long(normalized_input):
        bot_reply = "That's a lot of 'o's! Can you try something shorter?"

    elif is_playful(normalized_input):
        bot_reply = "That's a nice one! 😄 What's up?"

    elif is_question(normalized_input):
        bot_reply = "Hmm, that's a good question! Let me think about it."

    else:
        try:
            prompt = f"User: {normalized_input}\nBot: {last_bot_repsonse}"
            inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")
            attention_mask = torch.ones(inputs.shape, dtype=torch.long)

            response_ids = model.generate(
                inputs,
                attention_mask=attention_mask,
                max_length=1000,
                pad_token_id=tokenizer.eos_token_id
            )

            # Improved fallback if response is empty or weird
            if (
                not bot_reply.strip() or 
                any(word in bot_reply.lower() for word in ["u dogetipbot", "verify", "http", "reddit", "subreddit", "tip"])
                ):
                bot_reply = "Sorry, I’m still learning."
                last_bot_repsonse = bot_reply

        except Exception as e:
            print("Error:", e)
            bot_reply = "Sorry, I’m still learning."

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
