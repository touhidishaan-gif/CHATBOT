import re
import random

# --- AI State & Data ---
# Keep conversation_state as a stable dict object (do not fully clear it) so references remain valid.
conversation_state = {
    "scenario": None,
    "step_id": None,
    "user_data": {}
}

# Expanded vocabulary / definitions
DEFINITIONS = {
    "ubiquitous": {"def": "Present, appearing, or found everywhere.", "ex": "Mobile phones are ubiquitous these days."},
    "ephemeral": {"def": "Lasting for a very short time.", "ex": "The beauty of the cherry blossoms is ephemeral."},
    "resilience": {"def": "The capacity to recover quickly from difficulties; toughness.", "ex": "Her resilience in the face of adversity was admirable."},
    "eloquent": {"def": "Fluent or persuasive in speaking or writing.", "ex": "The speaker gave an eloquent speech about climate change."},
    "ambiguous": {"def": "Open to more than one interpretation; having a double meaning.", "ex": "The instructions were ambiguous, which led to confusion."},
    "integrity": {"def": "The quality of being honest and having strong moral principles.", "ex": "He is a man of great integrity."},
    # New additions
    "pragmatic": {"def": "Dealing with things sensibly and realistically in a way that is based on practical rather than theoretical considerations.", "ex": "A pragmatic approach often leads to quicker solutions."},
    "nuance": {"def": "A subtle difference in meaning, expression, or sound.", "ex": "Her argument captured the nuance of the situation."},
    "cogent": {"def": "(of an argument or case) clear, logical, and convincing.", "ex": "He made a cogent case for the new policy."},
    "serendipity": {"def": "The occurrence and development of events by chance in a happy or beneficial way.", "ex": "Finding the old letter was pure serendipity."},
}

# Expanded vocabulary boost mappings (longer phrases first)
VOCAB_BOOSTS = {
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
    # new boosts
    'very important': 'paramount', 'really good': 'remarkable', 'a lot': 'a great deal',
}

# Common grammar corrections with safer, well-formed regex patterns
GRAMMAR_CORRECTIONS = {
    r"\bi is\b": "I am", r"\bi has\b": "I have", r"\bi were\b": "I was",
    r"\bhe go\b": "he goes", r"\bhe do\b": "he does", r"\bhe have\b": "he has",
    r"\bshe go\b": "she goes", r"\bshe do\b": "she does", r"\bshe have\b": "she has",
    r"\bthey is\b": "they are", r"\bthey was\b": "they were", r"\bwe is\b": "we are",
    r"\bwe was\b": "we were", r"\bdefinately\b": "definitely", r"\bseperate\b": "separate",
    r"\bwich\b": "which", r"\buntill\b": "until", r"\bwierd\b": "weird",
    r"\bteh\b": "the", r"\boccured\b": "occurred", r"\bcalender\b": "calendar",
    r"\btommorow\b": "tomorrow", r"\barguement\b": "argument", r"\byour welcome\b": "you're welcome",
    r"\byoure\b": "you're", r"\btheyre\b": "they're", r"\bto much\b": "too much",
    r"\bit was to cold\b": "it was too cold", r"\bless people\b": "fewer people",
    r"\bthan me\b": "than I", r"\ba lot\b": "a lot", r"\bcould of\b": "could have",
    r"\bshould of\b": "should have", r"\bwould of\b": "would have",
    r"\bfor all intensive purposes\b": "for all intents and purposes",
    r"\bi could care less\b": "I couldn't care less",
}

# --- Utility Functions ---

def add_definition(word, meaning, example=None):
    """Add or update a definition at runtime."""
    DEFINITIONS[word.lower()] = {"def": meaning, "ex": example or ""}


def add_vocab_boost(phrase, replacement):
    """Add or update a vocabulary boost mapping."""
    VOCAB_BOOSTS[phrase.lower()] = replacement


def reset_conversation():
    """Clear current conversation but keep the state structure intact."""
    conversation_state['scenario'] = None
    conversation_state['step_id'] = None
    conversation_state['user_data'] = {}


def get_state():
    """Return a shallow copy of the conversation state for inspection/testing."""
    return conversation_state.copy()

# Helper to perform case-insensitive replacement while preserving the original case pattern

def _replace_preserve_case(text, pattern, replacement):
    def _repl(m):
        orig = m.group(0)
        # if all caps
        if orig.isupper():
            return replacement.upper()
        # if capitalized
        if orig[0].isupper():
            return replacement[0].upper() + replacement[1:]
        return replacement
    return re.sub(pattern, _repl, text, flags=re.IGNORECASE)

# --- Core text processing ---

def advanced_grammar_fix(text):
    """Clean basic grammar and common misspellings, return a cleaned, nicely punctuated string.
    This function intentionally keeps corrections conservative so we don't change user intent.
    """
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Apply corrections with preservation of case
    corrected = text
    for pattern, fix in GRAMMAR_CORRECTIONS.items():
        corrected = _replace_preserve_case(corrected, pattern, fix)

    # Ensure sentence starts with a capital
    corrected = corrected[0].upper() + corrected[1:]

    # Ensure sentence ends with punctuation
    if corrected[-1] not in ['.', '!', '?']:
        corrected += '.'

    return corrected


def advanced_vocab_boost(text):
    """Replace common words/phrases with stronger vocabulary. Operates conservatively.
    Longer phrases are replaced first to avoid partial matches.
    """
    if not text:
        return text
    boosted = text
    for phrase, replacement in sorted(VOCAB_BOOSTS.items(), key=lambda i: -len(i[0])):
        # Use word boundaries where appropriate
        boosted = re.sub(r'(?i)\\b' + re.escape(phrase) + r'\\b', lambda m: _match_case(replacement, m.group(0)), boosted)
    return boosted


def _match_case(replacement, original):
    # Preserve capitalization pattern
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


def explain_word(word):
    word_norm = word.lower().strip()
    if word_norm in DEFINITIONS:
        info = DEFINITIONS[word_norm]
        return f"'{word.capitalize()}' means: {info['def']}\n\nExample: \"{info['ex']}\""
    else:
        return f"Sorry, I don't have a definition for '{word}'. Try another word like 'resilience' or 'ephemeral'."

# --- Scenarios (unchanged data structure but safer access) ---
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
    # ... other scenarios unchanged for brevity ...
}

# --- Scenario engine with improved safety and matching ---

def _match_keywords(message, keywords):
    """Return True if any keyword matches as a whole word in message."""
    if not keywords:
        return False
    for kw in keywords:
        if re.search(r'(?i)\\b' + re.escape(kw) + r'\\b', message):
            return True
    return False


def scenario_chatbot_response(message, scenario_id):
    """Main driver for scenario-based conversations. Safer formatting and robust defaults.

    Returns a bot response string. Does not raise exceptions for bad input.
    """
    if not scenario_id or scenario_id not in SCENARIOS:
        return "Error: Invalid scenario selected."

    # Initialize or reset the scenario if different
    if conversation_state.get("scenario") != scenario_id:
        reset_conversation()
        conversation_state['scenario'] = scenario_id
        conversation_state['step_id'] = SCENARIOS[scenario_id]["start_step"]
        start_step_data = SCENARIOS[scenario_id]["steps"].get(conversation_state['step_id'], {})
        return start_step_data.get("bot", "Error: Could not start scenario.")

    scenario = SCENARIOS[scenario_id]
    current_step = scenario["steps"].get(conversation_state.get("step_id"), {})
    if not current_step:
        return "Error: Scenario step not found. Please restart."

    user_message_lower = message.lower() if isinstance(message, str) else ""

    # Data gathering: added more robust whole-word checks
    step_id = conversation_state.get("step_id")
    if step_id == "start" and scenario_id == "coffee_shop":
        if _match_keywords(user_message_lower, ["coffee", "latte", "cappuccino", "tea"]):
            # prefer the first matched keyword
            for drink in ["latte", "cappuccino", "coffee", "tea"]:
                if re.search(rf'(?i)\\b{drink}\\b', user_message_lower):
                    conversation_state['user_data']["drink"] = drink
                    break
    elif step_id == "size" and scenario_id == "coffee_shop":
        for sz in ["small", "medium", "large"]:
            if re.search(rf'(?i)\\b{sz}\\b', user_message_lower):
                conversation_state['user_data']["size"] = sz
                break
    # Additional scenario parsing can be added here with the same pattern

    # Determine next step
    next_step_id = None
    if "options" in current_step:
        for option in current_step.get("options", []):
            if _match_keywords(user_message_lower, option.get("keywords", [])):
                next_step_id = option.get("next_step")
                break
        if not next_step_id:
            # Provide clearer prompt listing the option keywords
            option_keywords = set(k for opt in current_step.get("options", []) for k in opt.get("keywords", []))
            return f"I didn't quite catch that. Please choose one of: {', '.join(sorted(option_keywords))}.\n\n" + current_step.get('bot', '')
    else:
        accept_input = current_step.get("accept_any", False) or not current_step.get("keywords")
        keywords_expected = current_step.get("keywords", [])
        keywords_match = False if accept_input else _match_keywords(user_message_lower, keywords_expected)
        if accept_input or keywords_match:
            next_step_id = current_step.get("next_step")
        else:
            if keywords_expected:
                return f"Please use words like: {', '.join(keywords_expected)}.\n\n" + current_step.get('bot', '')
            else:
                # No keywords expected and not accept_any -> accept as default
                next_step_id = current_step.get("next_step")

    # If no next step id, finish scenario
    if not next_step_id:
        feedback_msg = current_step.get("feedback", "Scenario complete. Well done!")
        reset_conversation()
        return feedback_msg

    # Advance state
    conversation_state['step_id'] = next_step_id
    next_step_data = scenario['steps'].get(next_step_id, {})
    next_bot_message = next_step_data.get('bot', '...')

    # Build message safely, replacing placeholders only if data exists
    try:
        if "{summary}" in next_bot_message:
            ud = conversation_state.get('user_data', {})
            vibe = ud.get('vibe', 'an enjoyable')
            activity = ud.get('activity', '')
            location = ud.get('location', '')
            activity_location = activity or location or "an interesting place"
            food = ud.get('food', 'some tasty options')
            summary = f"A {vibe} trip featuring {activity_location} with a focus on {food}."
            bot_response = next_bot_message.format(summary=summary)
        else:
            # Find placeholders and fill only when available
            expected_keys = re.findall(r"\{(.*?)\}", next_bot_message)
            safe_user_data = {}
            for k in expected_keys:
                safe_user_data[k] = conversation_state.get('user_data', {}).get(k, f"[{k}]")
            bot_response = next_bot_message.format(**safe_user_data)
    except Exception as e:
        # Fallback: return the raw message without formatting if anything goes wrong
        bot_response = next_step_data.get('bot', 'Okay, let\'s continue.')

    # Append feedback and reset if this is a final step
    if 'feedback' in next_step_data:
        bot_response += "\n\n" + next_step_data['feedback']
        reset_conversation()

    return bot_response


# --- Simple interactive demo function (for manual testing) ---
if __name__ == '__main__':
    print('Demo: start coffee_shop scenario')
    print(scenario_chatbot_response('Hi', 'coffee_shop'))
    print(scenario_chatbot_response('I will have a latte', 'coffee_shop'))
    print(scenario_chatbot_response('Medium', 'coffee_shop'))
    print(scenario_chatbot_response('No, thanks', 'coffee_shop'))
    print(scenario_chatbot_response('card', 'coffee_shop'))
    print('\nDefinitions sample:', explain_word('serendipity'))
