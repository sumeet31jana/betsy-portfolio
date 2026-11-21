import json
import os
import re
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "betsy-portfolio-dev-secret-key")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, "messages.json")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def save_message(entry: dict) -> None:
    """Append a validated contact form submission to messages.json."""
    messages = []
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, "r", encoding="utf-8") as file:
                messages = json.load(file)
        except (json.JSONDecodeError, OSError):
            messages = []

    messages.append(entry)
    with open(MESSAGES_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=2, ensure_ascii=False)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", current_year=datetime.now().year)


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not subject or not message:
        flash("Please complete all required fields before submitting.", "error")
        return redirect(url_for("home") + "#contact")

    if not EMAIL_REGEX.match(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home") + "#contact")

    submission = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
    }

    save_message(submission)
    print(f"[NEW INQUIRY] From: {name} <{email}> | Subject: {subject}")

    flash(
        f"Thank you, {name}. Your message has been received and logged.",
        "success",
    )
    return redirect(url_for("home") + "#contact")


if __name__ == "__main__":
    app.run(debug=True)