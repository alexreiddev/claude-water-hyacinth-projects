#!/usr/bin/env python3
"""
Flask backend for TechRec — AI Product Recommendation App.

Endpoints:
  GET  /                          Web app
  POST /api/session               Create session
  POST /api/chat                  Chat with Claude (SSE streaming)
  POST /api/recommend             Generate recommendations (SSE streaming)
  POST /api/search/youtube        Search YouTube for reviews
  POST /api/search/google         Search Google for reviews
  GET  /api/stores                List stores
  GET  /api/channels              List channels
  --- Admin (PIN protected) ---
  POST /admin/login
  GET  /admin/stores              List stores
  POST /admin/stores              Add store
  PUT  /admin/stores/<id>         Update store
  DELETE /admin/stores/<id>       Delete store
  GET  /admin/channels            List channels
  POST /admin/channels            Add channel
  PUT  /admin/channels/<id>       Update channel
  DELETE /admin/channels/<id>     Delete channel
  GET  /admin/config              Get config
  POST /admin/config              Save config
"""

import json
import os
import urllib.parse
import urllib.request
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, session

import claude_client
import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

# ── Helpers ───────────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        pin = db.get_config("admin_pin")
        if pin and not session.get("admin_authenticated"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


def sse(data: str | dict, event: str = "message") -> str:
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n"


def http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "TechRec/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


# ── Main app ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("app.html")


# ── Session ───────────────────────────────────────────────────────────────────

@app.route("/api/session", methods=["POST"])
def create_session():
    sid = db.create_session()
    return jsonify({"session_id": sid})


@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    messages = db.get_session_messages(session_id)
    rec = db.get_last_recommendation(session_id)
    return jsonify({"messages": messages, "recommendation": rec})


@app.route("/api/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    db.clear_session(session_id)
    return jsonify({"ok": True})


# ── Chat (SSE streaming) ──────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    session_id = data.get("session_id", "")
    user_message = data.get("message", "").strip()
    api_key = data.get("api_key") or os.getenv("ANTHROPIC_API_KEY", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    if not api_key:
        return jsonify({"error": "Anthropic API key not configured"}), 400

    # Persist user message
    if session_id:
        db.add_message(session_id, "user", user_message)

    # Get conversation history
    messages = db.get_session_messages(session_id) if session_id else [
        {"role": "user", "content": user_message}
    ]

    def generate():
        full_response = ""
        try:
            for chunk in claude_client.chat_stream(messages, api_key=api_key):
                full_response += chunk
                yield sse({"chunk": chunk})

            # Check if requirements are ready
            requirements = claude_client.parse_requirements(full_response)

            if session_id:
                # Strip the JSON marker from stored message
                clean = full_response.split("REQUIREMENTS_READY:")[0].strip()
                db.add_message(session_id, "assistant", clean or full_response)

            yield sse({
                "done": True,
                "full": full_response,
                "requirements": requirements,
            }, event="done")

        except RuntimeError as e:
            yield sse({"error": str(e)}, event="error")
        except Exception as e:
            yield sse({"error": f"Unexpected error: {e}"}, event="error")

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── Recommendations (SSE streaming) ──────────────────────────────────────────

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json or {}
    session_id = data.get("session_id", "")
    search_results = data.get("search_results", {})
    api_key = data.get("api_key") or os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key:
        return jsonify({"error": "Anthropic API key not configured"}), 400

    messages = db.get_session_messages(session_id) if session_id else []
    stores = db.list_stores(active_only=True)

    def generate():
        try:
            yield sse({"status": "Analyzing reviews and generating recommendations..."}, event="status")

            text = claude_client.get_recommendations(
                messages=messages,
                search_results=search_results,
                stores=stores,
                api_key=api_key,
            )

            recommendations = claude_client.parse_recommendations(text)

            if recommendations and session_id:
                # Extract requirements from last session message
                msgs = db.get_session_messages(session_id)
                requirements = {}
                for m in reversed(msgs):
                    req = claude_client.parse_requirements(m.get("content", ""))
                    if req:
                        requirements = req
                        break
                db.save_recommendation(session_id, requirements, recommendations)

            yield sse({
                "done": True,
                "text": text,
                "recommendations": recommendations,
                "stores": stores,
            }, event="done")

        except RuntimeError as e:
            yield sse({"error": str(e)}, event="error")
        except Exception as e:
            yield sse({"error": f"Unexpected error: {e}"}, event="error")

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── Search ────────────────────────────────────────────────────────────────────

@app.route("/api/search/youtube", methods=["POST"])
def search_youtube():
    data = request.json or {}
    query = data.get("query", "")
    api_key = data.get("youtube_api_key") or os.getenv("YOUTUBE_API_KEY", "")

    if not api_key:
        return jsonify({"results": [], "error": "YouTube API key not configured"})

    channels = db.list_channels(active_only=True)
    youtube_channels = [c for c in channels if c["platform"] == "youtube"]
    results = []

    for ch in youtube_channels[:5]:
        channel_id = ch.get("channel_id", "")
        if not channel_id:
            continue
        try:
            params = urllib.parse.urlencode({
                "part": "snippet",
                "channelId": channel_id,
                "q": query,
                "type": "video",
                "order": "relevance",
                "maxResults": 3,
                "key": api_key,
            })
            resp = http_get(f"https://www.googleapis.com/youtube/v3/search?{params}")
            for item in resp.get("items", []):
                snip = item.get("snippet", {})
                vid_id = item.get("id", {}).get("videoId", "")
                results.append({
                    "title": snip.get("title", ""),
                    "channel": snip.get("channelTitle", ch["name"]),
                    "description": snip.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "thumbnail": snip.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "published": snip.get("publishedAt", "")[:10],
                })
        except Exception:
            continue

    return jsonify({"results": results})


@app.route("/api/search/google", methods=["POST"])
def search_google():
    data = request.json or {}
    query = data.get("query", "")
    api_key = data.get("google_api_key") or os.getenv("GOOGLE_API_KEY", "")
    cx = data.get("google_cx") or os.getenv("GOOGLE_SEARCH_CX", "")

    if not api_key or not cx:
        return jsonify({"results": [], "error": "Google Search API key/CX not configured"})

    channels = db.list_channels(active_only=True)
    google_channels = [c for c in channels if c["platform"] == "google"]
    results = []

    for ch in google_channels[:5]:
        site = ch.get("site_search", "")
        if not site:
            continue
        try:
            site_query = f"{query} site:{site}"
            params = urllib.parse.urlencode({
                "key": api_key,
                "cx": cx,
                "q": site_query,
                "num": 3,
            })
            resp = http_get(f"https://www.googleapis.com/customsearch/v1?{params}")
            for item in resp.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "source": site,
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                })
        except Exception:
            continue

    return jsonify({"results": results})


# ── Public store/channel data ─────────────────────────────────────────────────

@app.route("/api/stores")
def api_stores():
    return jsonify(db.list_stores(active_only=True))


@app.route("/api/channels")
def api_channels():
    return jsonify(db.list_channels(active_only=True))


# ── Admin Auth ────────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def admin_login():
    pin = (request.json or {}).get("pin", "")
    stored = db.get_config("admin_pin")
    if stored and pin != stored:
        return jsonify({"error": "Incorrect PIN"}), 401
    session["admin_authenticated"] = True
    return jsonify({"ok": True})


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_authenticated", None)
    return jsonify({"ok": True})


# ── Admin: Stores ─────────────────────────────────────────────────────────────

@app.route("/admin/stores", methods=["GET"])
@admin_required
def admin_list_stores():
    return jsonify(db.list_stores())


@app.route("/admin/stores", methods=["POST"])
@admin_required
def admin_add_store():
    new_id = db.add_store(request.json or {})
    return jsonify({"id": new_id, "ok": True}), 201


@app.route("/admin/stores/<int:store_id>", methods=["PUT"])
@admin_required
def admin_update_store(store_id):
    db.update_store(store_id, request.json or {})
    return jsonify({"ok": True})


@app.route("/admin/stores/<int:store_id>", methods=["DELETE"])
@admin_required
def admin_delete_store(store_id):
    db.delete_store(store_id)
    return jsonify({"ok": True})


# ── Admin: Channels ───────────────────────────────────────────────────────────

@app.route("/admin/channels", methods=["GET"])
@admin_required
def admin_list_channels():
    return jsonify(db.list_channels())


@app.route("/admin/channels", methods=["POST"])
@admin_required
def admin_add_channel():
    new_id = db.add_channel(request.json or {})
    return jsonify({"id": new_id, "ok": True}), 201


@app.route("/admin/channels/<int:channel_id>", methods=["PUT"])
@admin_required
def admin_update_channel(channel_id):
    db.update_channel(channel_id, request.json or {})
    return jsonify({"ok": True})


@app.route("/admin/channels/<int:channel_id>", methods=["DELETE"])
@admin_required
def admin_delete_channel(channel_id):
    db.delete_channel(channel_id)
    return jsonify({"ok": True})


# ── Admin: Config ─────────────────────────────────────────────────────────────

@app.route("/admin/config", methods=["GET"])
@admin_required
def admin_get_config():
    return jsonify({
        "admin_pin":    db.get_config("admin_pin"),
        "youtube_key":  db.get_config("youtube_key"),
        "google_key":   db.get_config("google_key"),
        "google_cx":    db.get_config("google_cx"),
    })


@app.route("/admin/config", methods=["POST"])
@admin_required
def admin_save_config():
    data = request.json or {}
    for key in ("admin_pin", "youtube_key", "google_key", "google_cx"):
        if key in data:
            db.set_config(key, data[key])
    return jsonify({"ok": True})


# ── Boot ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.init_db()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"\n  TechRec server running at http://0.0.0.0:{port}")
    print(f"  On your phone, open: http://<your-computer-IP>:{port}\n")
    app.run(host=host, port=port, debug=debug)
