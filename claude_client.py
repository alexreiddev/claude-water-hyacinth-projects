#!/usr/bin/env python3
"""
Claude API integration for TechRec — AI Product Recommendation App.

Uses claude-opus-4-6 with adaptive thinking for intelligent
product requirement gathering and recommendation generation.
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are TechRec, an expert AI product advisor that helps users find the best tech products.

## Your Personality
- Friendly, knowledgeable, and concise
- Ask smart follow-up questions ONE at a time
- Be direct — don't pad responses with unnecessary text

## Conversation Flow

**Phase 1 — Understand the need:**
When a user expresses a product need, identify:
- Product category (laptop, smartphone, headphones, TV, etc.)
- Use case (gaming, work, college, content creation, etc.)
- Budget (parse naturally: "50k"=50,000 | "2 lakhs"=200,000 | "$500"=500 USD)

**Phase 2 — Narrow down (max 4 questions, one at a time):**
Ask focused questions to clarify:
- Performance level needed
- Portability / size preference
- Must-have features
- Brand preference (if any)
- Specific pain points or previous device issues

**Phase 3 — Signal readiness:**
When you have enough information (after gathering category + use case + budget + 2-3 key specs), output this EXACT block at the end of your message:

```
REQUIREMENTS_READY:{
  "category": "laptop",
  "use_case": "gaming at college",
  "budget_amount": 50000,
  "budget_currency": "INR",
  "budget_display": "₹50,000",
  "key_requirements": ["gaming GPU", "portable 15 inch", "good battery"],
  "preferences": {"portability": "important", "display": "15 inch"},
  "search_query": "gaming laptop under 50000 review 2024"
}
```

**Phase 4 — After search results provided:**
Analyze the provided review data and recommend products. Structure your response as:

```
RECOMMENDATIONS_JSON:{
  "summary": "2-sentence overview of the recommendation",
  "picks": [
    {
      "rank": 1,
      "name": "Full Product Name",
      "brand": "Brand",
      "price_range": "₹45,000–₹52,000",
      "rating": 8.5,
      "match_score": 95,
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2"],
      "best_for": "One line description of ideal user",
      "verdict": "Why this is ranked here"
    }
  ],
  "budget_pick": {
    "name": "Budget Product Name",
    "price_range": "₹38,000–₹42,000",
    "why": "Why it's a great budget option"
  },
  "avoid": "Product or brands to avoid and why",
  "final_recommendation": "1-2 sentence closing recommendation"
}
```

## Rules
- Never recommend more than 5 products
- Always include a budget pick if one exists
- Include real model names (e.g., "ASUS TUF Gaming F15 FX506LH", not just "ASUS laptop")
- Mention availability in the user's region
- If no search data is provided, use your training knowledge but note it may not be current
"""


def _client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


def chat_stream(messages: list[dict], api_key: str = ""):
    """
    Stream a chat response using claude-opus-4-6 with adaptive thinking.
    Yields text chunks as they arrive.
    """
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not configured")

    client = anthropic.Anthropic(api_key=key)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    yield event.delta.text


def get_recommendations(
    messages: list[dict],
    search_results: dict,
    stores: list[dict],
    api_key: str = "",
) -> str:
    """
    Generate structured product recommendations after search results are available.
    Returns the full assistant response text.
    """
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not configured")

    client = anthropic.Anthropic(api_key=key)

    # Build store context
    store_list = "\n".join(
        f"- {s['name']}: {s['url']} (search: {s.get('search_url_template', '')})"
        for s in stores if s.get("active")
    )

    # Build search context
    yt_results = search_results.get("youtube", [])
    g_results = search_results.get("google", [])

    search_context = ""
    if yt_results:
        search_context += "\n\n## YouTube Review Videos Found:\n"
        for r in yt_results[:8]:
            search_context += f"- [{r.get('title', '')}] by {r.get('channel', '')} — {r.get('url', '')}\n"
            if r.get("description"):
                search_context += f"  Summary: {r['description'][:200]}\n"

    if g_results:
        search_context += "\n\n## Tech Review Articles Found:\n"
        for r in g_results[:8]:
            search_context += f"- [{r.get('title', '')}] from {r.get('source', '')} — {r.get('url', '')}\n"
            if r.get("snippet"):
                search_context += f"  Excerpt: {r['snippet'][:200]}\n"

    inject_message = (
        "I've gathered review data from trusted tech channels. "
        "Please analyze this and provide your top product recommendations.\n"
        f"{search_context if search_context else 'Note: No external search results available — use your training knowledge.'}\n\n"
        f"## Available Purchase Stores:\n{store_list}\n\n"
        "Please provide your recommendations now in the RECOMMENDATIONS_JSON format."
    )

    full_messages = messages + [{"role": "user", "content": inject_message}]

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=full_messages,
    ) as stream:
        return stream.get_final_message().content[-1].text


def parse_requirements(text: str) -> dict | None:
    """Extract REQUIREMENTS_READY JSON from Claude's response."""
    marker = "REQUIREMENTS_READY:"
    idx = text.find(marker)
    if idx == -1:
        return None
    json_start = text.find("{", idx)
    json_end = text.rfind("}", json_start) + 1
    if json_start == -1 or json_end == 0:
        return None
    try:
        return json.loads(text[json_start:json_end])
    except json.JSONDecodeError:
        return None


def parse_recommendations(text: str) -> dict | None:
    """Extract RECOMMENDATIONS_JSON from Claude's response."""
    marker = "RECOMMENDATIONS_JSON:"
    idx = text.find(marker)
    if idx == -1:
        return None
    json_start = text.find("{", idx)
    json_end = text.rfind("}", json_start) + 1
    if json_start == -1 or json_end == 0:
        return None
    try:
        return json.loads(text[json_start:json_end])
    except json.JSONDecodeError:
        return None
