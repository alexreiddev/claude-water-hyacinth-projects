# Personal Networking Directory

Log people you meet and let Claude surface entrepreneurial opportunities, collaborations, and follow-up actions.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py setup   # enter your profile + API key
```

## Usage

| Command | What it does |
|---|---|
| `python app.py add` | Log a new person you met |
| `python app.py list` | Show all contacts |
| `python app.py list <search>` | Filter contacts |
| `python app.py view <id>` | See contact details + past analyses |
| `python app.py analyze <id>` | Run Claude opportunity analysis |
| `python app.py analyze <id> -c "I'm fundraising"` | Analysis with extra context |
| `python app.py network` | Analyze your whole network for patterns |
| `python app.py network -g "launch a SaaS"` | Network analysis toward a goal |
| `python app.py edit <id>` | Update a contact's data |
| `python app.py delete <id>` | Remove a contact |

## What Claude analyzes

For each contact:
- **Entrepreneurial opportunities** — business ideas you could build together
- **Immediate ways to help each other** — quick wins in the next 30 days
- **Their problems you could solve** — match their pain points to your work
- **Skills/resources to leverage** — what they uniquely bring
- **Suggested follow-up** — specific next steps with this person
- **Longer-term potential** — partnerships, investor angles, market access

For your full network:
- Cross-connection opportunities between contacts
- Emerging themes and market signals
- Best team assembly from your network
- Network gaps to fill
- Top 3 highest-leverage actions right now

## Data storage

Contacts and analyses are stored in `~/.personal_directory.db` (SQLite). Nothing leaves your machine except the Claude API calls.
