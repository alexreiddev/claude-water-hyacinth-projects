# TechRec — AI-Powered Product Recommendation App

An Android application (and companion web server) that uses Claude AI to help you find the best tech products. Tell it what you need in plain English — *"gaming laptop under 50k"* or *"best camera phone under ₹20,000"* — and it will ask smart follow-up questions, search trusted review channels, and recommend the best options with buy links.

---

## Features

| Feature | Description |
|---|---|
| **Natural language input** | *"I want a laptop for gaming, I have 50k"* |
| **Smart follow-up questions** | Asks targeted questions to narrow requirements |
| **Live review search** | Searches trusted YouTube + Google review sources |
| **AI recommendations** | Top picks with pros/cons, ratings, and match scores |
| **Buy links** | One-tap purchase links to admin-configured stores |
| **Admin panel** | Manage stores, review channels, and API keys |
| **Offline-capable** | Works without search APIs using Claude's knowledge |

---

## Architecture

```
┌──────────────────────────────────────────────┐
│  Android App (WebView)                        │
│  android-app/app/src/main/assets/index.html   │
│                                               │
│  Chat UI → smart questions → recommendations  │
│  Picks view: product cards + buy links        │
│  Admin panel: stores, channels, API keys      │
│                                               │
│  Direct API calls to:                         │
│  • api.anthropic.com  (Claude claude-opus-4-6) │
│  • googleapis.com     (YouTube + Search)      │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Optional: Python Web Server                  │
│                                               │
│  server.py       Flask API + streaming SSE    │
│  claude_client.py  Claude streaming client    │
│  db.py           SQLite (sessions, stores)    │
│  templates/app.html  Web UI                   │
└──────────────────────────────────────────────┘
```

---

## Android App (Primary)

The Android app is a fully self-contained WebView application — no server required.

### First Launch
1. Install the APK on your Android device
2. Enter your **Anthropic API key** when prompted
3. Get a free key at [console.anthropic.com](https://console.anthropic.com)
4. Start chatting!

### Optional: Enable Live Search
Add optional API keys in the **Admin** tab for richer recommendations:
- **YouTube Data API key** — searches channels like MKBHD, Dave2D in real-time
- **Google Custom Search key + CX** — searches RTINGS, Tom's Hardware, GSMArena, etc.

### Building the APK
```bash
cd android-app
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

---

## Web Server (Optional)

Run as a web app on your local network or deploy to the cloud.

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in ANTHROPIC_API_KEY in .env
python server.py
```

Then open `http://localhost:5000` (or `http://<your-ip>:5000` on mobile).

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/session` | Create a new chat session |
| `POST` | `/api/chat` | Stream a chat response (SSE) |
| `POST` | `/api/recommend` | Generate recommendations (SSE) |
| `POST` | `/api/search/youtube` | Search YouTube review channels |
| `POST` | `/api/search/google` | Search Google review sites |
| `GET` | `/api/stores` | List active buy stores |
| `GET` | `/api/channels` | List active review channels |
| `GET/POST` | `/admin/stores` | Manage stores (admin) |
| `GET/POST` | `/admin/channels` | Manage channels (admin) |
| `GET/POST` | `/admin/config` | Manage config & API keys (admin) |

---

## How It Works

### Conversation Flow
```
User: "gaming laptop, budget 50k"
      ↓
Claude: "Is portability important for college/travel?"
      ↓
User: "yes, I'll carry it daily"
      ↓
Claude: "Preferred display size — 14\", 15.6\", or larger?"
      ↓
User: "15 inch is fine"
      ↓
[Requirements complete → App searches YouTube & Google]
      ↓
[Claude analyzes review data → Ranks recommendations]
      ↓
Top Picks: Cards with pros/cons, ratings, buy buttons
```

### Pre-configured Review Sources

**YouTube Channels**: MKBHD, Dave2D, Linus Tech Tips, Mr Mobile, JerryRigEverything

**Review Websites**: RTINGS.com, Tom's Hardware, NotebookCheck, GSMArena, The Verge

All sources are fully admin-configurable.

---

## Admin Panel

Accessible in the app via the **Admin** tab.

### Manage Stores
Add retail stores where users can buy products:
- Name, URL, emoji logo
- Search URL template — use `{q}` as the query placeholder
  e.g. `https://www.amazon.in/s?k={q}`

**Default stores**: Amazon India, Flipkart, Croma, Reliance Digital, Vijay Sales

### Manage Review Channels
- **YouTube**: Paste the channel ID (from the channel's About page)
- **Google**: Add the site domain (e.g. `rtings.com`)

### API Keys
Stored securely in device localStorage (Android) or in-memory (server):
- Anthropic API key (required)
- YouTube Data API v3 key (optional)
- Google Custom Search API key + Engine CX ID (optional)

---

## Tech Stack

| Component | Technology |
|---|---|
| AI | Claude claude-opus-4-6 with adaptive thinking |
| Android | WebView + WebViewAssetLoader |
| Backend | Python 3, Flask, SQLite |
| Frontend | Vanilla HTML/CSS/JS — zero dependencies |
| Search | YouTube Data API v3, Google Custom Search API v1 |
