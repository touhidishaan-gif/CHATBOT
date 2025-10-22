from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import io

# Import the functions and state from our AI logic file
from ai_logic import (
    advanced_grammar_fix,
    advanced_vocab_boost,
    explain_word,
    scenario_chatbot_response,
    conversation_state # Import the state to handle chat continuity
)

# --- NEW: Import the functions from our Quiz logic file ---
from quiz_logic import (
    get_quiz_question,
    check_quiz_answer
)

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

# --- NEW: Route for the Quiz Page ---
@app.route("/quiz")
def quiz_page():
    """Renders the new Quiz page."""
    return render_template("quiz.html", page='quiz')


# --- API Endpoints ---
@app.route("/api/process", methods=["POST"])
def process_text():
    """Handles requests for grammar, vocab, and word explanations."""
    data = request.json
    text_input = data.get("text")
    action = data.get("action")

    if not text_input:
        return jsonify({"error": "No text provided."}), 400
    
    if action == "explain":
        result_text = explain_word(text_input)
    elif action == "grammar": 
        result_text = advanced_grammar_fix(text_input)
    elif action == "vocabulary": 
        result_text = advanced_vocab_boost(text_input)
    else: 
        return jsonify({"error": "Invalid action."}), 400
        
    return jsonify({"result": result_text})

@app.route("/api/chat", methods=["POST"])
def chat_with_tutor():
    """Handles requests for the scenario-based AI tutor."""
    data = request.json
    user_message = data.get("message")
    scenario_id = data.get("scenario")
    
    if not user_message and conversation_state["scenario"] != scenario_id:
        user_message = "start"
        
    if not user_message:
        return jsonify({"error": "No message provided."}), 400
        
    tutor_response = scenario_chatbot_response(user_message, scenario_id)
    return jsonify({"reply": tutor_response})
        
@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Handles text-to-speech requests."""
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

# --- NEW: API Routes for the Quiz ---
@app.route("/api/quiz/new", methods=["GET"])
def new_quiz_question():
    """Gets a new random question from the quiz logic."""
    question_data = get_quiz_question()
    return jsonify(question_data)

@app.route("/api/quiz/check", methods=["POST"])
def check_answer():
    """Checks the user's submitted answer."""
    data = request.json
    question_id = data.get("question_id")
    user_answer = data.get("answer")
    
    if not question_id or not user_answer:
        return jsonify({"error": "Missing question ID or answer."}), 400
        
    result = check_quiz_answer(question_id, user_answer)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

