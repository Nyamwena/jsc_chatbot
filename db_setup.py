import sqlite3

conn = sqlite3.connect('judicial_system.db')

# Create tables
conn.execute('''CREATE TABLE Judges (
    judge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    availability INTEGER
)''')

conn.execute('''CREATE TABLE Clerks (
    clerk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    availability INTEGER
)''')

conn.execute('''CREATE TABLE Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    judge_id INTEGER,
    date TEXT,
    time TEXT,
    FOREIGN KEY (judge_id) REFERENCES Judges (judge_id)
)''')

# Insert sample data
conn.execute("INSERT INTO Judges (name, specialization, availability) VALUES ('Judge A', 'child abuse', 1)")
conn.execute("INSERT INTO Clerks (name, department, availability) VALUES ('Clerk X', 'child abuse', 1)")
conn.commit()
conn.close()
print("Database setup complete!")
