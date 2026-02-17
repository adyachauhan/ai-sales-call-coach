# backend/agents/sentiment_agent.py

from __future__ import annotations
from typing import Dict, List


NEGATIVE_PHRASES = [
    "not interested", "stop calling", "don't call", "do not call",
    "waste of time", "annoying", "frustrated", "angry", "upset",
    "terrible", "bad experience", "hate", "complaint",
    "cancel", "refund", "no thanks", "not going to", "not worth"
]

POSITIVE_PHRASES = [
    "sounds good", "interested", "makes sense", "that works",
    "great", "perfect", "love it", "excited",
    "let's do it", "go ahead", "sign me up", "okay let's", "sure"
]

NEUTRAL_MARKERS = [
    "maybe", "not sure", "i'll think", "send me", "email me",
    "can you share", "what is the price", "how much", "details"
]


def _label(score: float) -> str:
    if score <= -2:
        return "Negative"
    if score >= 2:
        return "Positive"
    return "Neutral"


def sentiment_agent(transcript: str) -> Dict:
    """
    Lightweight sentiment detection with evidence.
    Not hardcoded to a single output: depends on transcript phrases.
    """
    t = (transcript or "").lower()

    score = 0.0
    evidence: List[str] = []

    for p in NEGATIVE_PHRASES:
        if p in t:
            score -= 2
            evidence.append(f"NEG: '{p}'")

    for p in POSITIVE_PHRASES:
        if p in t:
            score += 2
            evidence.append(f"POS: '{p}'")

    # If no strong signals, look for neutral markers (doesn't change score much)
    if score == 0:
        for p in NEUTRAL_MARKERS:
            if p in t:
                evidence.append(f"NEU: '{p}'")
                break

    label = _label(score)

    return {
        "sentiment_label": label,
        "sentiment_score": score,
        "sentiment_evidence": evidence[:5],  # keep it concise
    }