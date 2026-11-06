"""
Meridian Expenses — staff expense portal.

*** INTENTIONALLY VULNERABLE. TEACHING ARTEFACT. ***
Issued for CCT MSc Cybersecurity, Secure Programming and Scripting, CA1.
Do not deploy. Do not expose beyond localhost. Contains no real data.

There are more than six distinct, independently exploitable defects in this
file and its siblings. They are not marked.
"""
import hashlib
import os
import pickle
import sqlite3
import subprocess
import csv
import io
import re
import json

from flask import (Flask, g, redirect, render_template, request, session,
                   send_file, send_from_directory, url_for, Response)

app = Flask(__name__)
app.secret_key = "meridian-dev-key"          # fixed across every deployment
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

RECEIPTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "receipts"
)


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close(_exc):
    d = g.pop("db", None)
    if d is not None:
        d.close()


def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()


@app.route("/", methods=["GET"])
def index():
    if "uid" not in session:
        return redirect(url_for("login"))
    rows = db().execute(
        "SELECT * FROM claims WHERE user_id = %s ORDER BY id DESC" % session["uid"]
    ).fetchall()
    return render_template("index.html", claims=rows, user=session.get("name"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        q = "SELECT id, name, role FROM users WHERE username = ? AND password = ?"
        row = db().execute(q, (u, hash_pw(p))).fetchone()
        if row:
            session["uid"], session["name"], session["role"] = row["id"], row["name"], row["role"]
            return redirect(url_for("index"))
        exists = db().execute(
            "SELECT 1 FROM users WHERE username = ?", (u,)).fetchone()
        error = "Wrong password." if exists else "No such user."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/claim/<int:cid>")
def claim(cid):
    if "uid" not in session:
        return redirect(url_for("login"))

    row = db().execute(
        "SELECT * FROM claims WHERE id = ? AND user_id = ?",
        (cid, session["uid"])
    ).fetchone()

    if row is None:
        return "Not found", 404

    return render_template("claim.html", c=row)


@app.route("/claim/new", methods=["POST"])
def new_claim():
    db().execute(
        "INSERT INTO claims (user_id, merchant, amount, note, status) "
        "VALUES (?,?,?,?,'pending')",
        (session.get("uid"), request.form.get("merchant"),
         request.form.get("amount"), request.form.get("note")))
    db().commit()
    return redirect(url_for("index"))


@app.route("/receipt")
def receipt():
    if "uid" not in session:
        return redirect(url_for("login"))

    name = request.args.get("f", "")

    if not name:
        return "Bad Request", 400

    return send_from_directory(RECEIPTS_DIR, name)


@app.route("/export")
def export():
    # Require authentication
    if "uid" not in session:
        return redirect(url_for("login"))

    # Restrict exports to authorised roles
    if session.get("role") not in ("admin", "finance"):
        return "Forbidden", 403

    # Validate the month parameter
    month = request.args.get("month", "2026-09")

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        return "Invalid month format", 400

    # Retrieve records directly from SQLite
    rows = db().execute(
        "SELECT id, user_id, merchant, amount, note, status "
        "FROM claims ORDER BY id"
    ).fetchall()

    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id", "user_id", "merchant",
        "amount", "note", "status"
    ])

    for row in rows:
        writer.writerow(tuple(row))

    # Return downloadable CSV
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="expenses-{month}.csv"'
        }
    )


@app.route("/prefs", methods=["POST"])
def prefs():
    # Require authentication
    if "uid" not in session:
        return redirect(url_for("login"))

    blob = request.form.get("prefs", "")

    # Limit the size of submitted preferences
    if len(blob) > 4096:
        return "Preferences data too large", 413

    try:
        # Parse JSON instead of unsafe pickle data
        data = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        return "Invalid preferences format", 400

    # Only accept JSON objects
    if not isinstance(data, dict):
        return "Preferences must be a JSON object", 400

    # Validate permitted preference fields
    allowed_preferences = {
        "theme": {"light", "dark"},
        "language": {"en", "fr", "de"}
    }

    if not all(
        key in allowed_preferences
        and isinstance(value, str)
        and value in allowed_preferences[key]
        for key, value in data.items()
    ):
        return "Invalid preference values", 400

    session["prefs"] = data

    return redirect(url_for("index"))


@app.route("/admin/users")
def admin_users():
    # Require authentication
    if "uid" not in session:
        return redirect(url_for("login"))

    # Allow administrators only
    if session.get("role") != "admin":
        return "Forbidden", 403

    # Retrieve users after authorisation
    rows = db().execute(
        "SELECT id, username, name, role FROM users"
    ).fetchall()

    return render_template("admin.html", users=rows)


@app.route("/debug/config")
def debug_config():
    return {"secret_key": app.secret_key, "db": DB,
            "env": {k: v for k, v in os.environ.items() if "CCT" in k or "FLASK" in k}}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
