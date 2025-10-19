import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from gtts import gTTS
import io

# Load environment variables from .env file
load_dotenv()

# --- Google Gemini API Configuration ---
model = None
try:
    # Use the correct environment variable for Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    genai.configure(api_key=api_key)
    # Initialize the Gemini model with the correct name
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"FATAL: Error configuring Gemini API: {e}")


app = Flask(__name__)

# --- Page Routes ---
@app.route("/")
def grammar_page():
    """Renders the main Grammar Checker page."""
    return render_template("grammar_checker.html", page='grammar')

@app.route("/tutor")
def tutor_page():
    """Renders the AI Tutor chat page."""
    return render_template("tutor.html", page='tutor')

# --- API Endpoints ---
@app.route("/api/process", methods=["POST"])
def process_text():
    """API endpoint for grammar and vocabulary checks."""
    if not model:
        return jsonify({"error": "AI model is not configured. Check server logs."}), 500
        
    data = request.json
    text_input = data.get("text")
    action = data.get("action")

    if not text_input:
        return jsonify({"error": "No text provided."}), 400

    prompts = {
        "grammar": f"Correct the grammar and spelling mistakes in the following English text. Only return the corrected text, without any explanations or introductory phrases:\n\n---\n{text_input}\n---",
        "vocabulary": f"You are a vocabulary assistant. Rephrase the following English text to use more advanced and sophisticated vocabulary. Make it sound more professional and fluent. Only return the improved text, nothing else:\n\n---\n{text_input}\n---"
    }

    prompt = prompts.get(action)
    if not prompt:
        return jsonify({"error": "Invalid action."}), 400

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        return jsonify({"result": result_text})
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"error": "Failed to process text with the AI. Please check your API key and configuration."}), 500

@app.route("/api/chat", methods=["POST"])
def chat_with_tutor():
    """API endpoint for the AI Tutor chat."""
    if not model:
        return jsonify({"error": "AI model is not configured. Check server logs."}), 500

    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided."}), 400
        
    system_prompt = (
        "You are 'Lingo', a friendly and patient AI English tutor. "
        "Your goal is to help users practice their English conversation skills. "
        "Keep your responses concise and encouraging. Ask questions to keep the conversation going. "
        "If the user makes a grammar mistake, gently correct them by rephrasing their sentence correctly "
        "and then continue the conversation. For example, if they say 'I is happy', you can say 'That's great you are happy! What's making you feel that way?'"
    )
    
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nLingo:"

    try:
        response = model.generate_content(full_prompt)
        tutor_response = response.text.strip()
        return jsonify({"reply": tutor_response})
    except Exception as e:
        print(f"Gemini Chat Error: {e}")
        return jsonify({"error": "An error occurred with the AI tutor. Please try again."}), 500
        
@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """API endpoint for text-to-speech."""
    data = request.json
    text_to_speak = data.get('text')
    
    if not text_to_speak:
        return jsonify({"error": "No text provided for speech."}), 400

    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text_to_speak, lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return send_file(mp3_fp, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        print(f"gTTS Error: {e}")
        return jsonify({"error": "Failed to generate audio."}), 500

if __name__ == "__main__":
    app.run(debug=True)

