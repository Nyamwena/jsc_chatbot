import sqlite3

# Connect to the database
conn = sqlite3.connect('judicial_system.db')

def seed_database():
    cursor = conn.cursor()

    # Insert sample data into Judges table
    judges = [
        ("JUSTICE DUBE JUDGE", "child custody", 1),  # Available judge
        ("JUSTICE TAKUVA", "property disputes", 1),  # Available judge
        ("JUSTICE MATANDA", "criminal cases", 1),  # Available judge
        ("JUSTICE CHITAPI", "child abuse", 0)  # Unavailable judge
    ]
    cursor.executemany('''
        INSERT INTO Judges (name, specialization, availability)
        VALUES (?, ?, ?)
    ''', judges)

    # Insert sample data into Clerks table
    clerks = [
        ("G Moyo", "child custody", 1),  # Available clerk
        ("P Dube", "property disputes", 1),  # Available clerk
        ("S Baramasimbe", "criminal cases", 1),  # Available clerk
        ("Dan Munemo", "child abuse", 0)  # Unavailable clerk
    ]
    cursor.executemany('''
        INSERT INTO Clerks (name, department, availability)
        VALUES (?, ?, ?)
    ''', clerks)

    # Commit changes
    conn.commit()
    print("Database seeded successfully!")

# Seed the database
seed_database()

# Close the connection
conn.close()
