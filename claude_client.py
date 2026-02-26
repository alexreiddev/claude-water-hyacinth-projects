"""Claude AI integration for entrepreneurial opportunity mapping."""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _build_my_profile() -> str:
    parts = []
    if name := os.getenv("MY_NAME"):
        parts.append(f"Name: {name}")
    if skills := os.getenv("MY_SKILLS"):
        parts.append(f"Skills: {skills}")
    if industry := os.getenv("MY_INDUSTRY"):
        parts.append(f"Industry: {industry}")
    if projects := os.getenv("MY_CURRENT_PROJECTS"):
        parts.append(f"Current projects: {projects}")
    return "\n".join(parts) if parts else "Not specified"


def _contact_to_text(contact: dict) -> str:
    lines = [
        f"Name: {contact['name']}",
        f"Date met: {contact['date_met']}",
    ]
    if contact.get("where_met"):
        lines.append(f"Where met: {contact['where_met']}")
    if contact.get("profession"):
        lines.append(f"Profession: {contact['profession']}")
    if contact.get("industry"):
        lines.append(f"Industry: {contact['industry']}")
    if contact.get("skills"):
        lines.append(f"Skills: {', '.join(contact['skills'])}")
    if contact.get("interests"):
        lines.append(f"Interests: {', '.join(contact['interests'])}")
    if contact.get("resources"):
        lines.append(f"Resources/assets: {', '.join(contact['resources'])}")
    if contact.get("problems"):
        lines.append(f"Problems/pain points: {', '.join(contact['problems'])}")
    if contact.get("notes"):
        lines.append(f"Notes: {contact['notes']}")
    return "\n".join(lines)


def analyze_contact(contact: dict, extra_context: str = "") -> str:
    """Ask Claude to map out entrepreneurial opportunities with this contact."""
    my_profile = _build_my_profile()
    contact_text = _contact_to_text(contact)

    context_block = f"\nAdditional context: {extra_context}" if extra_context else ""

    prompt = f"""You are an entrepreneurial opportunity mapper. Given information about someone I recently met and my own profile, identify concrete ways we could collaborate, create value together, or help each other.

MY PROFILE:
{my_profile}

PERSON I MET:
{contact_text}{context_block}

Provide a structured analysis covering:

1. **Entrepreneurial Opportunities** — Specific business ideas or ventures we could build together, referencing their skills/resources and mine.

2. **Immediate Ways to Help Each Other** — Quick wins: introductions, advice, resources, or collaborations that could happen within the next 30 days.

3. **Their Problems I Could Solve** — Based on the pain points they mentioned, how could I (or something I'm building) address them?

4. **Skills/Resources I Should Leverage** — What they bring that would be uniquely valuable to me.

5. **Suggested Follow-Up** — Specific, actionable next steps with this person (what to say, what to propose, what to ask).

6. **Longer-Term Potential** — Bigger picture: strategic partnerships, investor angles, talent, or market access they could represent.

Be specific and practical. Avoid generic advice. If information is limited, flag what data would sharpen the analysis."""

    message = get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def analyze_network(contacts: list[dict], goal: str = "") -> str:
    """Analyze the full network for patterns and cross-connection opportunities."""
    if not contacts:
        return "No contacts to analyze yet."

    contact_summaries = []
    for c in contacts:
        summary = f"- {c['name']} ({c.get('profession', 'unknown')}): skills={c.get('skills', [])}, industry={c.get('industry', '')}"
        contact_summaries.append(summary)

    contacts_text = "\n".join(contact_summaries)
    my_profile = _build_my_profile()
    goal_block = f"\nMy current goal: {goal}" if goal else ""

    prompt = f"""You are an entrepreneurial network analyst. Review this person's contact network and surface patterns, synergies, and hidden opportunities.

MY PROFILE:
{my_profile}{goal_block}

MY NETWORK ({len(contacts)} contacts):
{contacts_text}

Provide:

1. **Cross-Connection Opportunities** — Pairs or groups of contacts who should meet each other (and why).

2. **Emerging Themes** — Patterns in skills, industries, or problems that suggest a market opportunity.

3. **Team Assembly** — If I wanted to start something new, which contacts form the best founding team or advisory board?

4. **Network Gaps** — What types of people am I missing that would accelerate my goals?

5. **Top 3 Highest-Leverage Actions** — The single best moves I can make with this network right now.

Be specific and reference contacts by name."""

    message = get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
