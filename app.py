from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import PyPDF2
import re
import json
import time
import random
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Load NLP pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Load sentence transformer for semantic search
embedder = SentenceTransformer('all-MiniLM-L6-v2')

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

# Extract text from PDF files
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

# Preprocess text
def preprocess_text(raw_text):
    stop_words = set(stopwords.words('english'))
    raw_text = re.sub(r'\s+', ' ', raw_text)  # Remove extra spaces
    raw_text = re.sub(r'[^\w\s]', '', raw_text)  # Remove special characters
    sentences = sent_tokenize(raw_text)
    cleaned_sentences = []
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        filtered_words = [word for word in words if word not in stop_words]
        cleaned_sentences.append(' '.join(filtered_words))
    return cleaned_sentences

# Perform semantic search to find relevant content
def semantic_search(query, documents, top_k=5):
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    doc_embeddings = embedder.encode(documents, convert_to_tensor=True)

    hits = util.semantic_search(query_embedding, doc_embeddings, top_k=top_k)
    results = [documents[hit['corpus_id']] for hit in hits[0]]
    return results

# Answer questions using the QA pipeline
def answer_question(question, context):
    response = qa_pipeline(question=question, context=context)
    return response['answer']

# Assign judge and clerk based on case type
def assign_judge_clerk(case_type):
    cursor = conn.cursor()

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

# Load preprocessed PDF data once
pdf_files = ["data/guardianship.pdf", "data/maintanance_act.pdf", "data/children_act.pdf"]
preprocessed_data = {}
for file in pdf_files:
    text = extract_text_from_pdf(file)
    preprocessed_data[file] = preprocess_text(text)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    # Flatten preprocessed data for semantic search
    all_sentences = [sentence for doc in preprocessed_data.values() for sentence in doc]

    # Show a random "Thinking" message during processing
    thinking_messages = ["Analyzing your query...", "Processing your request...", "Fetching relevant data..."]
    thinking_message = random.choice(thinking_messages)
    print(f"DEBUG: {thinking_message}")

    time.sleep(1.5)  # Simulate processing delay

    # Semantic search to find relevant context
    relevant_contexts = semantic_search(user_input, all_sentences)
    context = " ".join(relevant_contexts[:2])  # Combine top 2 matches

    # Process user input
    if "assign" in user_input.lower():
        case_type = user_input.lower()  # Simplified case type detection
        assignment = assign_judge_clerk(case_type)

        if assignment:
            response = f"Judge {assignment['judge_name']} and Clerk {assignment['clerk_name']} are assigned to handle your case."
            response += "\nWould you like to schedule an appointment?"
        else:
            response = "No available judge or clerk for this case type at the moment. Please try again later."
    elif "schedule" in user_input.lower():
        response = schedule_appointment(1, 1, "John Doe", "2024-12-15", "10:00 AM")
    else:
        try:
            response = answer_question(user_input, context)
        except Exception as e:
            print(f"Error during question answering: {e}")
            response = "Sorry, there was an issue processing your request."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
