import os
import json
import re
from typing import List
import requests
from dotenv import load_dotenv

from .models import DocumentAnalysis, Entity

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OWL_ALPHA_MODEL = os.getenv("OWL_ALPHA_MODEL", "openrouter/owl-alpha")

def _naive_sentiment(text: str) -> str:
    pos = ["good", "great", "positive", "excellent", "happy", "benefit"]
    neg = ["bad", "poor", "negative", "terrible", "unhappy", "loss"]
    t = text.lower()
    score = sum(t.count(w) for w in pos) - sum(t.count(w) for w in neg)
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"

def _naive_summary(text: str, max_sentences: int = 3) -> str:
    # Split into sentences heuristically
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    parts = [p.replace("\n", " ").strip() for p in parts if p.strip()]
    return " ".join(parts[:max_sentences])

def _pad_entities(entities: List[Entity]) -> List[Entity]:
    result = entities[:5]
    while len(result) < 5:
        result.append(Entity(type="UNKNOWN", text="", confidence=0.0))
    return result

def analyze_with_openrouter(text: str) -> DocumentAnalysis:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system = (
        "You are an assistant that MUST return JSON matching the schema:"
        "{document_type, sentiment, entities: [{type,text,confidence}], summary}."
        "Only output the JSON object, no explanatory text."
    )

    user = (
        "Given the following document text, identify document_type (short noun), sentiment"
        "(positive|neutral|negative), exactly 5 key entities with confidence 0-1, and a ~3-sentence summary."
        "Respond with a single JSON object matching the Pydantic schema.\n\nText:\n" + text
    )

    payload = {
        "model": OWL_ALPHA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 1200,
        "temperature": 0.0,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Expect content at choices[0].message.content
    content = None
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = data.get("choices", [{}])[0].get("text")

    if not content:
        raise RuntimeError("No content returned from OpenRouter")

    # Try to parse JSON from the model output
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        # Try to find the first JSON object in text
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            parsed = json.loads(m.group(0))

    if parsed is None:
        raise RuntimeError("Could not parse JSON from model response")

    # Validate via Pydantic
    return DocumentAnalysis.model_validate(parsed)

def analyze_document(text: str) -> DocumentAnalysis:
    # Prefer OpenRouter if configured, else fallback to naive analysis
    if OPENROUTER_API_KEY:
        try:
            return analyze_with_openrouter(text)
        except Exception:
            pass

    # Fallback (deterministic, useful for local testing without API key)
    sentiment = _naive_sentiment(text)
    summary = _naive_summary(text)

    # Very naive entity extraction: capture capitalized word groups
    cand = re.findall(r"\b([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+)*)\b", text)
    entities = []
    seen = set()
    for c in cand:
        if c.lower() in seen:
            continue
        seen.add(c.lower())
        entities.append(Entity(type="MISC", text=c, confidence=0.25))
        if len(entities) >= 5:
            break

    entities = _pad_entities(entities)
    return DocumentAnalysis(document_type="unknown", sentiment=sentiment, entities=entities, summary=summary)
