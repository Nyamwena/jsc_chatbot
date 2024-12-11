from transformers import pipeline
import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load the NLP pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Database connection
conn = sqlite3.connect('judicial_system.db', check_same_thread=False)

def preprocess_input(user_input):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(user_input.lower())
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

def answer_question(question, context):
    response = qa_pipeline(question=question, context=context)
    return response['answer']

def assign_judge_clerk(case_type):
    cursor = conn.cursor()
    cursor.execute("SELECT judge_id FROM Judges WHERE specialization = ? AND availability = 1 LIMIT 1", (case_type,))
    judge = cursor.fetchone()
    cursor.execute("SELECT clerk_id FROM Clerks WHERE department = ? AND availability = 1 LIMIT 1", (case_type,))
    clerk = cursor.fetchone()
    if judge and clerk:
        return {"judge_id": judge[0], "clerk_id": clerk[0]}
    return "No available judge or clerk at the moment."

def schedule_appointment(judge_id, date, time):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Appointments (judge_id, date, time) VALUES (?, ?, ?)", (judge_id, date, time))
    conn.commit()
    return "Appointment booked successfully!"
