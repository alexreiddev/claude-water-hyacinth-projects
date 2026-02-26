#!/usr/bin/env python3
"""
Flask web server — mobile-first interface for the Personal Directory.

Run:
  python server.py

Then open http://localhost:5000 on any device on the same network,
or expose it publicly with ngrok / a cloud deploy.
"""

import os
import threading
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, Response
)
from dotenv import load_dotenv
import db
import claude_client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

PIN = os.getenv("ACCESS_PIN", "")   # empty = no auth required


# ── auth ──────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if PIN and not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("pin") == PIN:
            session["authenticated"] = True
            return redirect(request.args.get("next") or url_for("index"))
        flash("Incorrect PIN", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── main routes ───────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    contacts = db.list_contacts(search)
    return render_template("index.html", contacts=contacts, search=search)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        def get_list(key):
            raw = request.form.get(key, "")
            return [x.strip() for x in raw.split(",") if x.strip()]

        contact_id = db.add_contact({
            "name":       request.form.get("name", "").strip(),
            "date_met":   request.form.get("date_met", ""),
            "where_met":  request.form.get("where_met", ""),
            "profession": request.form.get("profession", ""),
            "industry":   request.form.get("industry", ""),
            "skills":     get_list("skills"),
            "interests":  get_list("interests"),
            "resources":  get_list("resources"),
            "problems":   get_list("problems"),
            "notes":      request.form.get("notes", ""),
        })
        flash(f"Contact saved!", "success")

        if request.form.get("auto_analyze") == "1":
            return redirect(url_for("analyze", contact_id=contact_id))
        return redirect(url_for("view", contact_id=contact_id))

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("add.html", today=today)


@app.route("/contact/<int:contact_id>")
@login_required
def view(contact_id):
    contact = db.get_contact(contact_id)
    if not contact:
        flash("Contact not found", "error")
        return redirect(url_for("index"))
    analyses = db.get_analyses(contact_id)
    return render_template("view.html", contact=contact, analyses=analyses)


@app.route("/contact/<int:contact_id>/edit", methods=["GET", "POST"])
@login_required
def edit(contact_id):
    contact = db.get_contact(contact_id)
    if not contact:
        flash("Contact not found", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        def get_list(key):
            raw = request.form.get(key, "")
            return [x.strip() for x in raw.split(",") if x.strip()]

        db.update_contact(contact_id, {
            "name":       request.form.get("name", "").strip(),
            "date_met":   request.form.get("date_met", ""),
            "where_met":  request.form.get("where_met", ""),
            "profession": request.form.get("profession", ""),
            "industry":   request.form.get("industry", ""),
            "skills":     get_list("skills"),
            "interests":  get_list("interests"),
            "resources":  get_list("resources"),
            "problems":   get_list("problems"),
            "notes":      request.form.get("notes", ""),
        })
        flash("Contact updated", "success")
        return redirect(url_for("view", contact_id=contact_id))

    # Pre-fill list fields as comma-separated strings for the form
    contact["skills_str"]    = ", ".join(contact.get("skills", []))
    contact["interests_str"] = ", ".join(contact.get("interests", []))
    contact["resources_str"] = ", ".join(contact.get("resources", []))
    contact["problems_str"]  = ", ".join(contact.get("problems", []))
    return render_template("edit.html", contact=contact)


@app.route("/contact/<int:contact_id>/delete", methods=["POST"])
@login_required
def delete(contact_id):
    contact = db.get_contact(contact_id)
    if contact:
        db.delete_contact(contact_id)
        flash(f"Deleted {contact['name']}", "success")
    return redirect(url_for("index"))


@app.route("/contact/<int:contact_id>/analyze")
@login_required
def analyze(contact_id):
    contact = db.get_contact(contact_id)
    if not contact:
        flash("Contact not found", "error")
        return redirect(url_for("index"))
    extra_context = request.args.get("context", "")
    return render_template(
        "analyze.html", contact=contact, extra_context=extra_context
    )


@app.route("/contact/<int:contact_id>/analyze/stream")
@login_required
def analyze_stream(contact_id):
    """Server-sent events stream for live Claude output."""
    contact = db.get_contact(contact_id)
    if not contact:
        return "data: ERROR: Contact not found\n\n", 404

    extra_context = request.args.get("context", "")
    result_holder = {}
    error_holder = {}

    def run():
        try:
            result_holder["text"] = claude_client.analyze_contact(
                contact, extra_context=extra_context
            )
        except Exception as e:
            error_holder["msg"] = str(e)

    t = threading.Thread(target=run)
    t.start()

    def generate():
        t.join()
        if error_holder:
            yield f"data: ERROR:{error_holder['msg']}\n\n"
        else:
            text = result_holder.get("text", "")
            db.save_analysis(contact_id, text, context=extra_context)
            # Send in chunks so UI can render progressively
            for i in range(0, len(text), 80):
                chunk = text[i:i+80].replace("\n", "\\n")
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/network")
@login_required
def network():
    contacts = db.list_contacts()
    goal = request.args.get("goal", "")
    return render_template("network.html", contacts=contacts, goal=goal, count=len(contacts))


@app.route("/network/analyze/stream")
@login_required
def network_stream():
    """Server-sent events stream for live network analysis."""
    goal = request.args.get("goal", "")
    contacts = db.list_contacts()

    result_holder = {}
    error_holder = {}

    def run():
        try:
            result_holder["text"] = claude_client.analyze_network(contacts, goal=goal)
        except Exception as e:
            error_holder["msg"] = str(e)

    t = threading.Thread(target=run)
    t.start()

    def generate():
        t.join()
        if error_holder:
            yield f"data: ERROR:{error_holder['msg']}\n\n"
        else:
            text = result_holder.get("text", "")
            for i in range(0, len(text), 80):
                chunk = text[i:i+80].replace("\n", "\\n")
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    db.init_db()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")   # 0.0.0.0 = reachable on LAN
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"\n  Personal Directory running at http://0.0.0.0:{port}")
    print(f"  On your phone, open: http://<your-computer-IP>:{port}\n")
    app.run(host=host, port=port, debug=debug)
