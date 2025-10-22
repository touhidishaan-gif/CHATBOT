import random

# --- Quiz Data Store ---
# All questions for the quiz are stored here.
QUIZ_DATA = [
    {
        "id": "q1",
        "question": "Which sentence is grammatically correct?",
        "options": [
            "He don't like vegetables.",
            "He doesn't like vegetables.",
            "He not like vegetables.",
            "He don't likes vegetables."
        ],
        "answer": "He doesn't like vegetables."
    },
    {
        "id": "q2",
        "question": "What is a synonym for 'ephemeral'?",
        "options": [
            "Permanent",
            "Beautiful",
            "Fleeting",
            "Strong"
        ],
        "answer": "Fleeting"
    },
    {
        "id": "q3",
        "question": "Choose the correct word: 'I am going to ______ my book on the table.'",
        "options": [
            "lay",
            "lie",
            "lain",
            "lied"
        ],
        "answer": "lay"
    },
    {
        "id": "q4",
        "question": "What does 'ubiquitous' mean?",
        "options": [
            "Rare",
            "Found everywhere",
            "Weak",
            "Intelligent"
        ],
        "answer": "Found everywhere"
    },
    {
        "id": "q5",
        "question": "Which is correct: 'its' or 'it's'?",
        "options": [
            "'Its' is possessive, 'it's' means 'it is'.",
            "'It's' is possessive, 'its' means 'it is'.",
            "They are interchangeable.",
            "Only 'its' is a real word."
        ],
        "answer": "'Its' is possessive, 'it's' means 'it is'."
    },
    {
        "id": "q6",
        "question": "The team is ______ new strategy for the project.",
        "options": [
            "devising",
            "devicing",
            "devising of",
            "devise"
        ],
        "answer": "devising"
    },
    {
        "id": "q7",
        "question": "What is the opposite of 'resilience'?",
        "options": [
            "Strength",
            "Fragility",
            "Honesty",
            "Loudness"
        ],
        "answer": "Fragility"
    },

    # --- NEW QUESTIONS ADDED BELOW ---

    {
        "id": "q8",
        "question": "Choose the correct sentence:",
        "options": [
            "There are less tasks to do today.",
            "There are fewer tasks to do today.",
            "There is fewer tasks to do today.",
            "There is less tasks to do today."
        ],
        "answer": "There are fewer tasks to do today."
    },
    {
        "id": "q9",
        "question": "What does the idiom 'bite the bullet' mean?",
        "options": [
            "To eat something quickly",
            "To get injured",
            "To go to sleep",
            "To face a difficult situation with courage"
        ],
        "answer": "To face a difficult situation with courage"
    },
    {
        "id": "q10",
        "question": "She has been working here ______ 2018.",
        "options": [
            "for",
            "since",
            "by",
            "at"
        ],
        "answer": "since"
    },
    {
        "id": "q11",
        "question": "What is a synonym for 'ambiguous'?",
        "options": [
            "Clear",
            "Loud",
            "Unclear or vague",
            "Angry"
        ],
        "answer": "Unclear or vague"
    },
    {
        "id": "q12",
        "question": "If I ______ you, I would study for the test.",
        "options": [
            "was",
            "am",
            "were",
            "be"
        ],
        "answer": "were"
    },
    {
        "id": "q13",
        "question": "The meeting was ______ because the manager was sick.",
        "options": [
            "put off",
            "put on",
            "put in",
            "put by"
        ],
        "answer": "put off"
    },
    {
        "id": "q14",
        "question": "Select the correct use of 'affect' and 'effect'.",
        "options": [
            "The rain will effect the game.",
            "The rain will affect the game.",
            "The rain will have an affect on the game.",
            "The affect of the rain was bad."
        ],
        "answer": "The rain will affect the game."
    },

    # --- NEW QUESTIONS ADDED BELOW ---

    {
        "id": "q15",
        "question": "What does 'to beat around the bush' mean?",
        "options": [
            "To speak directly",
            "To avoid saying something directly",
            "To clear a path in a forest",
            "To be very busy"
        ],
        "answer": "To avoid saying something directly"
    },
    {
        "id": "q16",
        "question": "He ______ to the store when his phone rang.",
        "options": [
            "was driving",
            "drove",
            "is driving",
            "driven"
        ],
        "answer": "was driving"
    },
    {
        "id": "q17",
        "question": "What is a synonym for 'meticulous'?",
        "options": [
            "Messy",
            "Quick",
            "Very careful and precise",
            "Angry"
        ],
        "answer": "Very careful and precise"
    },
    {
        "id": "q18",
        "question": "The book is on the table, ______ it?",
        "options": [
            "is",
            "isn't",
            "does",
            "doesn't"
        ],
        "answer": "isn't"
    },
    {
        "id": "q19",
        "question": "I have ______ money than you.",
        "options": [
            "less",
            "fewer",
            "many",
            "little"
        ],
        "answer": "less"
    },
    {
        "id": "q20",
        "question": "What does 'to break the ice' mean?",
        "options": [
            "To make something colder",
            "To end a relationship",
            "To make people feel more comfortable in a social situation",
            "To start an argument"
        ],
        "answer": "To make people feel more comfortable in a social situation"
    }
]

# --- Quiz Logic Functions ---

def get_quiz_question():
    """
    Selects a random question from the list.
    We send the 'id' to the frontend to check the answer later.
    """
    question_data = random.choice(QUIZ_DATA)
    return {
        "question_id": question_data["id"],
        "question": question_data["question"],
        "options": question_data["options"]
    }

def check_quiz_answer(question_id, user_answer):
    """
    Checks if the user's answer is correct for the given question ID.
    """
    for question_data in QUIZ_DATA:
        if question_data["id"] == question_id:
            is_correct = (user_answer == question_data["answer"])
            return {
                "is_correct": is_correct,
                "correct_answer": question_data["answer"]
            }
    
    # Fallback in case the question ID isn't found
    return {"is_correct": False, "correct_answer": "Error: Question not found."}

