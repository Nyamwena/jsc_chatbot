from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime

# Load the NLP pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Database connection
conn = sqlite3.connect('judicial_system.db', check_same_thread=False)

# Ensure database tables exist
def setup_database():
    cursor = conn.cursor()

    # Judges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Judges (
            judge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialization TEXT,
            availability INTEGER  -- 1 = Available, 0 = Unavailable
        )
    ''')

    # Clerks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clerks (
            clerk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            availability INTEGER
        )
    ''')

    # Appointments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            litigant_name TEXT,
            judge_id INTEGER,
            clerk_id INTEGER,
            date TEXT,
            time TEXT,
            FOREIGN KEY (judge_id) REFERENCES Judges (judge_id),
            FOREIGN KEY (clerk_id) REFERENCES Clerks (clerk_id)
        )
    ''')

    conn.commit()

setup_database()

# Preprocess user input
def preprocess_input(user_input):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(user_input.lower())
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

# Answer questions using the QA pipeline
def answer_question(question, context):
    response = qa_pipeline(question=question, context=context)
    return response['answer']

# Assign judge and clerk based on case type
def assign_judge_clerk(case_type):
    cursor = conn.cursor()
    case_type = 'child custody'
    # Find available judge
    cursor.execute('''
        SELECT judge_id, name FROM Judges 
        WHERE specialization = ? AND availability = 1 
        LIMIT 1
    ''', (case_type,))
    judge = cursor.fetchone()

    # Find available clerk
    cursor.execute('''
        SELECT clerk_id, name FROM Clerks 
        WHERE department = ? AND availability = 1 
        LIMIT 1
    ''', (case_type,))
    clerk = cursor.fetchone()

    if judge and clerk:
        return {"judge_id": judge[0], "judge_name": judge[1], "clerk_id": clerk[0], "clerk_name": clerk[1]}
    elif judge:
        return {"judge_id": judge[0], "judge_name": judge[1], "clerk_id": None, "clerk_name": None}
    elif clerk:
        return {"judge_id": None, "judge_name": None, "clerk_id": clerk[0], "clerk_name": clerk[1]}
    else:
        return None

# Schedule an appointment
def schedule_appointment(judge_id, clerk_id, litigant_name, date, time):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Appointments (litigant_name, judge_id, clerk_id, date, time)
        VALUES (?, ?, ?, ?, ?)
    ''', (litigant_name, judge_id, clerk_id, date, time))
    conn.commit()
    return "Your appointment has been scheduled successfully."

# Flask app setup
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    context = open('data/judiciary_context.txt').read()

    # Detect case type (basic string matching or NLP can be added here)
    if "assign" in user_input.lower():
        case_type = preprocess_input(user_input)  # Example preprocessing
        assignment = assign_judge_clerk(case_type)

        if assignment:
            response = f"Judge {assignment['judge_name']} and Clerk {assignment['clerk_name']} are assigned to handle your case."
            response += "\nWould you like to schedule an appointment?"
        else:
            response = "No available judge or clerk for this case type at the moment. Please try again later."
    elif "schedule" in user_input.lower():
        response = schedule_appointment(1, 1, "John Doe", "2024-12-15", "10:00 AM")
    else:
        response = answer_question(user_input, context)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
