import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "patients.db"


def ensure_column(cursor, table_name: str, column_name: str, ddl_type: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing = {row[1] for row in cursor.fetchall()}
    if column_name not in existing:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_type}")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        age INTEGER,
        gender TEXT,
        mobile_number TEXT,
        city TEXT,
        mri_prediction TEXT,
        audio_prediction TEXT,
        cognitive_score REAL,
        final_prediction TEXT,
        confidence REAL,
        date TEXT
    )
    """)

    ensure_column(cursor, "patients", "mobile_number", "TEXT")
    ensure_column(cursor, "patients", "city", "TEXT")

    conn.commit()
    conn.close()


def insert_patient(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients (
        patient_name, age, gender, mobile_number, city,
        mri_prediction, audio_prediction,
        cognitive_score, final_prediction,
        confidence, date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["patient_name"],
        data["age"],
        data["gender"],
        data["mobile_number"],
        data["city"],
        data["mri_prediction"],
        data["audio_prediction"],
        data["cognitive_score"],
        data["final_prediction"],
        data["confidence"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_patients():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return rows
