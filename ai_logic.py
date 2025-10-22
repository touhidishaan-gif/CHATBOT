import re
import random

# --- AI State & Data ---

# Global state to hold simple conversation memory
conversation_state = {
    "scenario": None,
    "step_id": None,
    "user_data": {}
}

# All dictionaries for AI behavior are now stored here
DEFINITIONS = {
    "ubiquitous": {"def": "Present, appearing, or found everywhere.", "ex": "Mobile phones are ubiquitous these days."},
    "ephemeral": {"def": "Lasting for a very short time.", "ex": "The beauty of the cherry blossoms is ephemeral."},
    "resilience": {"def": "The capacity to recover quickly from difficulties; toughness.", "ex": "Her resilience in the face of adversity was admirable."},
    "eloquent": {"def": "Fluent or persuasive in speaking or writing.", "ex": "The speaker gave an eloquent speech about climate change."},
    "ambiguous": {"def": "Open to more than one interpretation; having a double meaning.", "ex": "The instructions were ambiguous, which led to confusion."},
    "integrity": {"def": "The quality of being honest and having strong moral principles.", "ex": "He is a man of great integrity."},
}

SCENARIOS = {
    "coffee_shop": {
        "title": "Ordering Coffee", "start_step": "start", "steps": {
            "start": {"bot": "Hello! Welcome to Lingo Coffee. What can I get for you today?", "keywords": ["coffee", "latte", "cappuccino", "tea"], "next_step": "size"},
            "size": {"bot": "Excellent choice. What size would you like for your {drink}? We have small, medium, or large.", "keywords": ["small", "medium", "large"], "next_step": "extra"},
            "extra": {"bot": "One {size} {drink}, coming right up. Would you like anything else? Perhaps a croissant or muffin?", "keywords": ["yes", "no", "croissant", "muffin"], "next_step": "payment"},
            "payment": {"bot": "Alright. Your total is $5.75. Will that be cash or card?", "keywords": ["cash", "card"], "next_step": "end"},
            "end": {"bot": "Thank you. We'll have your order ready in a moment!", "feedback": "Great job! You successfully ordered a drink. This conversation is complete."}
        }
    },
    "job_interview": {
        "title": "Job Interview", "start_step": "intro", "steps": {
            "intro": {"bot": "Thank you for coming in today. To start, could you tell me a little bit about yourself?", "accept_any": True, "next_step": "strength"},
            "strength": {"bot": "That's very interesting. Based on your background, what would you say is your greatest strength?", "accept_any": True, "next_step": "weakness"},
            "weakness": {"bot": "A valuable skill. On the other hand, what is an area you would like to improve on?", "accept_any": True, "next_step": "questions"},
            "questions": {"bot": "Thank you for your honesty. Finally, do you have any questions for me about the company or the role?", "keywords": ["question", "company", "culture", "team", "no"], "next_step": "end"},
            "end": {"bot": "That's a great question. [The bot gives a brief, generic answer]. Thank you for your time. We'll be in touch soon.", "feedback": "Excellent work! You handled the interview questions professionally."}
        }
    },
    "weekend_trip": {
        "title": "Plan a Weekend Trip", "start_step": "intro", "steps": {
            "intro": {"bot": "Let's plan a perfect weekend trip! What kind of vibe are you looking for: relaxing, adventurous, or a city exploration?", "options": [{"keywords": ["relax", "beach", "calm"], "next_step": "relax_choice"}, {"keywords": ["adventure", "hike", "exciting"], "next_step": "adventure_choice"}, {"keywords": ["city", "museum", "explore"], "next_step": "city_choice"}]},
            "relax_choice": {"bot": "A relaxing trip sounds wonderful. Do you prefer a quiet beach or a cozy cabin in the mountains?", "options": [{"keywords": ["beach", "sand", "ocean"], "next_step": "food_choice"}, {"keywords": ["cabin", "mountain", "forest"], "next_step": "food_choice"}]},
            "adventure_choice": {"bot": "An adventure! Excellent. Are you more interested in hiking up a mountain or kayaking on a river?", "options": [{"keywords": ["hike", "mountain", "climb"], "next_step": "food_choice"}, {"keywords": ["kayak", "river", "water"], "next_step": "food_choice"}]},
            "city_choice": {"bot": "A city exploration it is! Would you rather spend your time visiting historical museums or trying out trendy new restaurants?", "options": [{"keywords": ["museum", "history", "art"], "next_step": "food_choice"}, {"keywords": ["restaurant", "food", "eat"], "next_step": "food_choice"}]},
            "food_choice": {"bot": "Great choice. And for food, are you looking for budget-friendly local eats or a fine dining experience?", "options": [{"keywords": ["budget", "local", "cheap"], "next_step": "summary"}, {"keywords": ["dining", "fancy", "expensive"], "next_step": "summary"}]},
            "summary": {"bot": "Okay, I've got the perfect plan! Based on your choices, here is your ideal weekend trip: {summary}", "feedback": "It was fun planning with you! Your trip sounds amazing. This scenario is complete."}
        }
    },
    "doctor_appointment": {
        "title": "Doctor's Appointment", "start_step": "intro", "steps": {
            "intro": {"bot": "Hello, Lingo Clinic. How can I help you today?", "keywords": ["appointment", "doctor", "see"], "next_step": "reason"},
            "reason": {"bot": "Of course. To help you, could you briefly tell me the reason for your visit? For example, a check-up, a headache, or a cough.", "accept_any": True, "next_step": "when"},
            "when": {"bot": "I see. And when would be a good time for you? We have openings tomorrow morning or the day after in the afternoon.", "options": [{"keywords": ["tomorrow", "morning"], "next_step": "confirm"}, {"keywords": ["day after", "afternoon"], "next_step": "confirm"}]},
            "confirm": {"bot": "Perfect. I've booked you an appointment for {time}. We will see you then. Is there anything else I can help with?", "keywords": ["no", "thank you", "thanks"], "next_step": "end"},
            "end": {"bot": "You're welcome. Have a great day and we look forward to seeing you.", "feedback": "Excellent! You clearly communicated your needs and scheduled an appointment. This is a very useful skill."}
        }
    }
}

# --- AI Core Functions ---

def advanced_grammar_fix(text):
    if not text: return ""
    text = text.strip()
    if not text: return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ['.', '!', '?']: text += '.'
    corrections = {
        r'\bi is\b': 'I am', r'\bi am goes\b': 'I go', r'\bi has\b': 'I have',
        r'\bi were\b': 'I was', r'\bhe go\b': 'he goes', r'\bhe do\b': 'he does',
        r'\bhe have\b': 'he has', r'\bshe go\b': 'she goes', r'\bshe do\b': 'she does',
        r'\bshe have\b': 'she has', r'\bthey is\b': 'they are', r'\bthey was\b': 'they were',
        r'\bwe is\b': 'we are', r'\bwe was\b': 'we were', r'\bdefinately\b': 'definitely',
        r'\bseperate\b': 'separate', r'\breceive\b': 'receive', r'\baccomodate\b': 'accommodate',
        r'\bwich\b': 'which', r'\buntill\b': 'until', r'\bwierd\b': 'weird',
        r'\bteh\b': 'the', r'\boccured\b': 'occurred', r'\bcalender\b': 'calendar',
        r'\btommorow\b': 'tomorrow', r'\barguement\b': 'argument', r'\byour welcome\b': "you're welcome",
        r'\byoure\b': "you're", r"\bits\b (?!')": "it's", r'\bthere listening\b': "they're listening",
        r'\btheyre\b': "they're", r'\bto much\b': 'too much', r'\it was to cold\b': 'it was too cold',
        r'\bless\b people': 'fewer people', r'\bthan me\b': 'than I', r'\bwho\b goes there': 'who goes there',
        r'\bwhom\b should I ask': 'whom should I ask', r'\ba lot\b': 'a lot', r'\bcould of\b': 'could have',
        r'\bshould of\b': 'should have', r'\bwould of\b': 'would have', r'\bfor all intensive purposes\b': 'for all intents and purposes',
        r'\bi could care less\b': 'I couldn\'t care less',
    }
    corrected_text = text
    for error, fix in corrections.items():
        corrected_text = re.sub(error, fix, corrected_text, flags=re.IGNORECASE)
    return corrected_text

def advanced_vocab_boost(text):
    boosts = {
        'very good': 'outstanding', 'very happy': 'ecstatic', 'very sad': 'despondent',
        'very big': 'colossal', 'very small': 'infinitesimal', 'very tired': 'exhausted',
        'very smart': 'brilliant', 'very angry': 'furious', 'very beautiful': 'exquisite',
        'very bad': 'atrocious', 'good': 'excellent', 'great': 'fantastic',
        'happy': 'elated', 'sad': 'dejected', 'big': 'enormous', 'small': 'minuscule',
        'fast': 'rapid', 'slow': 'sluggish', 'important': 'crucial', 'interesting': 'fascinating',
        'tired': 'fatigued', 'smart': 'intelligent', 'nice': 'charming', 'bad': 'abysmal',
        'walk': 'stroll', 'run': 'sprint', 'look': 'glance', 'see': 'observe',
        'think': 'ponder', 'say': 'exclaim', 'make': 'create', 'do': 'execute',
        'start': 'commence', 'end': 'conclude', 'help': 'assist', 'get': 'obtain',
        'use': 'utilize', 'show': 'demonstrate', 'ask': 'inquire', 'tell': 'inform',
    }
    boosted_text = text
    for phrase, replacement in sorted(boosts.items(), key=lambda item: len(item[0]), reverse=True):
        boosted_text = re.sub(r'\b' + re.escape(phrase) + r'\b', replacement, boosted_text, flags=re.IGNORECASE)
    return boosted_text

def explain_word(word):
    word = word.lower().strip()
    if word in DEFINITIONS:
        info = DEFINITIONS[word]
        return f"'{word.capitalize()}' means: {info['def']}\n\nExample: \"{info['ex']}\""
    else:
        return f"Sorry, I don't have a definition for '{word}'. Try another word like 'resilience' or 'ephemeral'."

# --- THE FIX IS HERE: More robust logic ---
def scenario_chatbot_response(message, scenario_id):
    global conversation_state
    if not scenario_id or scenario_id not in SCENARIOS:
        return "Error: Invalid scenario selected."

    if conversation_state["scenario"] != scenario_id:
        conversation_state.update({"scenario": scenario_id, "step_id": SCENARIOS[scenario_id]["start_step"], "user_data": {}})
        return SCENARIOS[scenario_id]["steps"][conversation_state["step_id"]]["bot"]

    scenario = SCENARIOS[scenario_id]
    current_step = scenario["steps"][conversation_state["step_id"]]
    user_message_lower = message.lower()

    # --- FIX 1: More Robust Data Gathering ---
    step_id = conversation_state["step_id"]
    if step_id == "start" and scenario_id == "coffee_shop":
        if "coffee" in user_message_lower: conversation_state["user_data"]["drink"] = "coffee"
        elif "latte" in user_message_lower: conversation_state["user_data"]["drink"] = "latte"
        elif "cappuccino" in user_message_lower: conversation_state["user_data"]["drink"] = "cappuccino"
        elif "tea" in user_message_lower: conversation_state["user_data"]["drink"] = "tea"
    if step_id == "size" and scenario_id == "coffee_shop":
        if "small" in user_message_lower: conversation_state["user_data"]["size"] = "small"
        elif "medium" in user_message_lower: conversation_state["user_data"]["size"] = "medium"
        elif "large" in user_message_lower: conversation_state["user_data"]["size"] = "large"
    if step_id == "intro" and scenario_id == "weekend_trip": conversation_state["user_data"]["vibe"] = message
    if "beach" in user_message_lower: conversation_state["user_data"]["location"] = "a quiet beach"
    if "cabin" in user_message_lower: conversation_state["user_data"]["location"] = "a cozy mountain cabin"
    if "hike" in user_message_lower: conversation_state["user_data"]["activity"] = "hiking"
    if "kayak" in user_message_lower: conversation_state["user_data"]["activity"] = "kayaking"
    if "museum" in user_message_lower: conversation_state["user_data"]["activity"] = "visiting museums"
    if "restaurant" in user_message_lower: conversation_state["user_data"]["activity"] = "trying new restaurants"
    if "budget" in user_message_lower or "local" in user_message_lower or "cheap" in user_message_lower:
        conversation_state["user_data"]["food"] = "budget-friendly local eats"
    if "dining" in user_message_lower or "fancy" in user_message_lower or "expensive" in user_message_lower:
        conversation_state["user_data"]["food"] = "a fine dining experience"
    if "tomorrow" in user_message_lower: conversation_state["user_data"]["time"] = "tomorrow morning at 10 AM"
    if "day after" in user_message_lower: conversation_state["user_data"]["time"] = "the day after tomorrow at 2 PM"

    next_step_id = None
    if "options" in current_step:
        for option in current_step["options"]:
            if any(keyword in user_message_lower for keyword in option["keywords"]):
                next_step_id = option["next_step"]; break
        if not next_step_id:
            return f"(I didn't quite catch that. Could you choose one of the options? Let's try again...) {current_step['bot']}"
    else:
        if current_step.get("accept_any", False):
            next_step_id = current_step.get("next_step")
        elif any(keyword in user_message_lower for keyword in current_step.get("keywords", [])):
             next_step_id = current_step.get("next_step")
        else:
            return f"(I was hoping for a bit more detail. Let's try that question again...) {current_step['bot']}"

    if not next_step_id:
        conversation_state["scenario"] = None
        return current_step.get("feedback", "Scenario complete. Well done!")

    conversation_state["step_id"] = next_step_id
    next_bot_message = scenario["steps"][next_step_id]["bot"]

    if "{summary}" in next_bot_message:
        ud = conversation_state['user_data']
        summary = f"A {ud.get('vibe', 'city')} trip featuring {ud.get('activity', ud.get('location', ''))} with a focus on {ud.get('food', 'local eats')}."
        next_bot_message = next_bot_message.format(summary=summary)
    
    bot_response = next_bot_message.format(**(conversation_state.get("user_data", {})))

    # --- FIX 2: Check if the next step is the final one and combine messages ---
    final_step = scenario["steps"][next_step_id]
    if "feedback" in final_step:
        bot_response += "\n\n" + final_step["feedback"]
        conversation_state["scenario"] = None # End the scenario
    
    return bot_response

