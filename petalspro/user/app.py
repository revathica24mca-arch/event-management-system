from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import os

# BASE_DIR is the folder containing app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# TEMPLATE_DIR points to the 'templates' folder inside BASE_DIR
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# DATABASE path
DB_NAME = os.path.join(BASE_DIR, "database.db")

# Initialize Flask with the correct template folder
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = "your_secret_key"

# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Bookings table
    c.execute("""CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        date TEXT,
        details TEXT
    )""")
    # Feedback table
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        event TEXT,
        date TEXT,
        rating INTEGER,
        message TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ROUTES ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "manager" and password == "1234":
            session["user"] = username
            return redirect(url_for("manager_dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- MANAGER DASHBOARD ----------------
@app.route("/manager")
def manager_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM feedback ORDER BY id DESC")
    feedbacks = [dict(r) for r in c.fetchall()]

    conn.close()
    return render_template("manager.html", bookings=bookings, feedbacks=feedbacks)

# ---------------- CUSTOMER BOOKING ----------------
@app.route("/", methods=["GET", "POST"])
def book_event():
    if request.method == "POST":
        booking = (
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["date"],
            request.form["details"]
        )
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, phone, email, date, details) VALUES (?, ?, ?, ?, ?)", booking)
        conn.commit()
        conn.close()
        return redirect(url_for("thank_you"))
    return render_template("book.html")

@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")  # make sure the filename matches exactly

# ---------------- CUSTOMER FEEDBACK ----------------
# User submits feedback
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        name = request.form["name"]
        event = request.form["event"]
        date = request.form["date"]
        rating = request.form["rating"]
        message = request.form["feedback"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedback (name, event, date, rating, message) VALUES (?, ?, ?, ?, ?)",
            (name, event, date, rating, message)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("thank_you"))  # after submission → thank you page

    return render_template("feedback.html")  # show form if GET

# ---------------- MANAGER FEEDBACKS ONLY ----------------
# Manager sees all feedback
@app.route("/managerfeed")
def manager_feedbacks():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM feedback ORDER BY id DESC")
    feedbacks = [dict(r) for r in c.fetchall()]
    conn.close()

    return render_template("manager_feedback.html", feedbacks=feedbacks)




# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
