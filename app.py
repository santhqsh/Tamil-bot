import openai
import requests
from flask import Flask, request, jsonify

# Flask app
app = Flask(__name__)

# Instagram API Credentials (Set these as Railway Environment Variables)
VERIFY_TOKEN = "tamilchatbot123"  # Set any random string
ACCESS_TOKEN = "your_facebook_page_access_token"
OPENAI_API_KEY = "your_openai_api_key"

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

# Verify Webhook
@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

# Detect emotion from user messages
def detect_emotion(user_input):
    prompt = f"Analyze this message and classify the emotion: {user_input}\nCategories: Happy, Sad, Flirty, Angry, Neutral"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Classify the text as Happy, Sad, Flirty, Angry, or Neutral."},
                  {"role": "user", "content": user_input}]
    )
    
    return response["choices"][0]["message"]["content"].strip()

# Generate Tamil chatbot responses
def generate_tamil_response(user_input):
    emotion = detect_emotion(user_input)

    if emotion == "Happy":
        prompt = f"Reply in a fun and energetic Tamil style: {user_input}"
    elif emotion == "Sad":
        prompt = f"Reply in a comforting and caring Tamil style: {user_input}"
    elif emotion == "Flirty":
        prompt = f"Reply in a playful and teasing Tamil style: {user_input}"
    elif emotion == "Angry":
        prompt = f"Reply in a calm and diplomatic Tamil style: {user_input}"
    else:
        prompt = f"Reply naturally in Tamil: {user_input}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a Tamil-speaking person chatting naturally."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

# Handle incoming Instagram messages
@app.route("/", methods=["POST"])
def receive_message():
    data = request.json
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            message_text = messaging["message"]["text"]

            # Generate AI reply
            reply_text = generate_tamil_response(message_text)
            send_message(sender_id, reply_text)

    return "OK", 200

# Send message back to Instagram DM
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}

    requests.post(url, json=payload, headers=headers)

# Run Flask app
if __name__ == "__main__":
    app.run(port=5000)