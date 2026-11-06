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

from flask import (Flask, g, redirect, render_template, request, session,
                   send_file, url_for)

app = Flask(__name__)
app.secret_key = "meridian-dev-key"          # fixed across every deployment
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")


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
    row = db().execute("SELECT * FROM claims WHERE id = ?", (cid,)).fetchone()
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
    name = request.args.get("f", "")
    return send_file(os.path.join("receipts", name))


@app.route("/export")
def export():
    month = request.args.get("month", "2026-09")
    out = "/tmp/expenses-%s.csv" % month
    subprocess.call(
        "sqlite3 %s '.mode csv' '.once %s' 'SELECT * FROM claims'" % (DB, out),
        shell=True)
    return send_file(out, as_attachment=True)


@app.route("/prefs", methods=["POST"])
def prefs():
    blob = request.form.get("prefs", "")
    data = pickle.loads(bytes.fromhex(blob))
    session["prefs"] = data
    return redirect(url_for("index"))


@app.route("/admin/users")
def admin_users():
    rows = db().execute("SELECT id, username, name, role FROM users").fetchall()
    return render_template("admin.html", users=rows)


@app.route("/debug/config")
def debug_config():
    return {"secret_key": app.secret_key, "db": DB,
            "env": {k: v for k, v in os.environ.items() if "CCT" in k or "FLASK" in k}}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
