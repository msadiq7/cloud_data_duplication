from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import csv
import io
from datetime import datetime

app = Flask(__name__)

DATABASE = "deduplication.db"


# -----------------------------
# DATABASE
# -----------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# VALIDATION
# -----------------------------

def validate_record(name, email, phone):

    errors = []

    name = name.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if not name:
        errors.append("Name is required.")

    elif len(name) < 2:
        errors.append("Name must contain at least 2 characters.")

    if not email:
        errors.append("Email is required.")

    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("Invalid email address.")

    if not phone:
        errors.append("Phone number is required.")

    elif not re.match(r"^[0-9]{10}$", phone):
        errors.append("Phone number must contain exactly 10 digits.")

    return errors


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def index():

    return render_template("index.html")


# -----------------------------
# GET RECORDS
# -----------------------------

@app.route("/api/records", methods=["GET"])
def get_records():

    conn = get_db()

    records = conn.execute("""
        SELECT * FROM records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(record) for record in records])


# -----------------------------
# STATISTICS
# -----------------------------

@app.route("/api/stats", methods=["GET"])
def get_stats():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) FROM records"
    ).fetchone()[0]

    conn.close()

    return jsonify({
        "total": total
    })


# -----------------------------
# ADD RECORD
# -----------------------------

@app.route("/api/records", methods=["POST"])
def add_record():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")

    # Validate
    errors = validate_record(name, email, phone)

    if errors:
        return jsonify({
            "success": False,
            "type": "validation",
            "message": "Invalid data.",
            "errors": errors
        }), 400

    email = email.strip().lower()

    conn = get_db()

    # Duplicate check
    existing = conn.execute(
        "SELECT * FROM records WHERE email = ?",
        (email,)
    ).fetchone()

    if existing:

        conn.close()

        return jsonify({
            "success": False,
            "type": "duplicate",
            "message": "Duplicate record detected. This email already exists."
        }), 409

    # Save record
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
        INSERT INTO records
        (name, email, phone, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name.strip(),
        email,
        phone.strip(),
        created_at
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Record verified and saved successfully."
    })


# -----------------------------
# DELETE RECORD
# -----------------------------

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):

    conn = get_db()

    record = conn.execute(
        "SELECT * FROM records WHERE id = ?",
        (record_id,)
    ).fetchone()

    if not record:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Record not found."
        }), 404

    conn.execute(
        "DELETE FROM records WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Record deleted successfully."
    })


# -----------------------------
# CSV UPLOAD
# -----------------------------

@app.route("/api/upload", methods=["POST"])
def upload_csv():

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "message": "No file uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a CSV file."
        }), 400

    if not file.filename.lower().endswith(".csv"):

        return jsonify({
            "success": False,
            "message": "Only CSV files are supported."
        }), 400

    try:

        content = file.read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))

        required_columns = {"name", "email", "phone"}

        if not required_columns.issubset(
            set(reader.fieldnames or [])
        ):

            return jsonify({
                "success": False,
                "message": "CSV must contain: name, email, phone"
            }), 400

        conn = get_db()

        inserted = 0
        duplicates = 0
        invalid = 0

        for row in reader:

            name = row.get("name", "").strip()
            email = row.get("email", "").strip().lower()
            phone = row.get("phone", "").strip()

            errors = validate_record(
                name,
                email,
                phone
            )

            if errors:

                invalid += 1
                continue

            existing = conn.execute(
                "SELECT id FROM records WHERE email = ?",
                (email,)
            ).fetchone()

            if existing:

                duplicates += 1
                continue

            created_at = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            conn.execute("""
                INSERT INTO records
                (name, email, phone, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                created_at
            ))

            inserted += 1

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "CSV processing completed.",
            "inserted": inserted,
            "duplicates": duplicates,
            "invalid": invalid
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Error processing CSV.",
            "error": str(e)
        }), 500


# -----------------------------
# START APPLICATION
# -----------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )