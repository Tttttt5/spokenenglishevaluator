import re
from typing import Dict, Any, List

# ---------- CONFIG / CONSTANTS ---------- #

SALUTATION_NORMAL = ["hi", "hello"]
SALUTATION_GOOD = [
    "good morning",
    "good afternoon",
    "good evening",
    "good day",
    "hello everyone"
]
SALUTATION_EXCELLENT_PHRASES = [
    "i am excited to introduce",
    "i'm excited to introduce",
    "feeling great",
    "i am very excited",
    "i'm very excited"
]

MUST_HAVE_KEYWORDS = [
    "name",      # e.g. "my name is"
    "age",
    "class",
    "school",
    "family",
    "hobby",
    "hobbies",
    "interests"
]

GOOD_TO_HAVE_KEYWORDS = [
    "from",          # origin / place
    "goal",
    "dream",
    "ambition",
    "unique",
    "strength",
    "achievement",
    "fun fact"
]

FILLER_WORDS = [
    "um", "uh", "like", "you know", "so", "actually", "basically", "right",
    "i mean", "well", "kinda", "sort of", "okay", "ok", "hmm", "ah"
]

# very simple sentiment lexicon for "Engagement"
POSITIVE_WORDS = {
    "happy", "excited", "glad", "enjoy", "enjoying", "love", "like",
    "confident", "grateful", "thankful", "proud", "interested",
    "passionate", "fun", "great"
}
NEGATIVE_WORDS = {
    "boring", "tired", "sad", "nervous", "scared", "anxious",
    "worried", "hate", "dislike"
}

# ---------- HELPERS ---------- #

def clean_text(text: str) -> str:
    """Lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()

def tokenize_words(text: str) -> List[str]:
    return clean_text(text).split()

# ---------- SALUTATION ---------- #

def detect_salutation(text: str) -> Dict[str, Any]:
    t = clean_text(text)

    if any(phrase in t for phrase in SALUTATION_EXCELLENT_PHRASES):
        return {"score": 100, "level": "Excellent"}

    if any(phrase in t for phrase in SALUTATION_GOOD):
        return {"score": 75, "level": "Good"}

    if any(word in t.split() for word in SALUTATION_NORMAL):
        return {"score": 50, "level": "Normal"}

    return {"score": 0, "level": "None"}

# ---------- KEYWORDS ---------- #

def detect_keywords(text: str) -> Dict[str, Any]:
    t = clean_text(text)

    must_found: List[str] = []
    good_found: List[str] = []
    points = 0

    for kw in MUST_HAVE_KEYWORDS:
        if kw in t:
            points += 4
            must_found.append(kw)

    for kw in GOOD_TO_HAVE_KEYWORDS:
        if kw in t:
            points += 2
            good_found.append(kw)

    max_points = 30
    points = min(points, max_points)
    score = (points / max_points) * 100 if max_points > 0 else 0

    return {
        "score": score,
        "points": points,
        "must_have_found": must_found,
        "good_to_have_found": good_found
    }

# ---------- FLOW ---------- #

def basic_flow_check(text: str) -> Dict[str, Any]:
    """
    Very simple flow check:
    - salutation should come before name
    - name/basic details before hobbies/goals
    """
    t = clean_text(text)

    salutation_index = min(
        [t.find(x) for x in SALUTATION_NORMAL + SALUTATION_GOOD if x in t] or [-1]
    )
    name_index = min(
        [idx for idx in [t.find("my name is"), t.find("i am ")] if idx != -1] or [-1]
    )
    hobby_index = t.find("hobby")
    goal_index = t.find("goal")

    order_ok = True

    if salutation_index != -1 and name_index != -1:
        if salutation_index > name_index:
            order_ok = False

    for idx in [hobby_index, goal_index]:
        if idx != -1 and name_index != -1 and idx < name_index:
            order_ok = False

    score = 100 if order_ok else 40

    return {
        "score": score,
        "order_ok": order_ok
    }

# ---------- SPEECH RATE (APPROX) ---------- #

def speech_rate_score(word_count: int) -> Dict[str, Any]:
    """
    We only have transcript, no real audio duration.
    For now we approximate WPM ≈ word_count (assuming ~1 minute intro).
    You can replace this with real duration later.
    """
    wpm = word_count  # proxy assumption

    if wpm > 161:
        score = 0
        band = "Too fast"
    elif 141 <= wpm <= 160:
        score = 40
        band = "Fast"
    elif 111 <= wpm <= 140:
        score = 100
        band = "Ideal"
    elif 81 <= wpm <= 110:
        score = 60
        band = "Slow"
    else:  # < 80
        score = 20
        band = "Too slow"

    return {"score": score, "wpm_estimate": wpm, "band": band}

# ---------- GRAMMAR (HEURISTIC) ---------- #

def grammar_score(text: str) -> Dict[str, Any]:
    """
    Simple heuristic grammar score (no external grammar library):
    - Penalize very long sentences with few punctuation marks.
    - Penalize repeated 'and' chaining as a proxy for run-on sentences.
    """
    words = tokenize_words(text)
    total_words = len(words) or 1

    # Count sentences by '.', '!', '?'
    sentence_splits = re.split(r"[.!?]+", text)
    sentence_count = len([s for s in sentence_splits if s.strip()]) or 1

    avg_sentence_length = total_words / sentence_count

    # Count "and" overuse as a proxy for run-on / weak structure
    and_count = words.count("and")

    # Start from a base score and subtract penalties
    score = 90.0

    # Penalize very long sentences
    if avg_sentence_length > 25:
        score -= 25
    elif avg_sentence_length > 18:
        score -= 15
    elif avg_sentence_length > 12:
        score -= 5

    # Penalize too many "and"
    if and_count > 5:
        score -= 20
    elif and_count > 3:
        score -= 10

    # Clamp between 0 and 100
    score = max(0.0, min(100.0, score))

    return {
        "score": score,
        "avg_sentence_length": avg_sentence_length,
        "and_count": and_count,
        "note": "Heuristic grammar score (no external grammar tool)."
    }

# ---------- VOCABULARY (TTR) ---------- #

def vocabulary_score(text: str) -> Dict[str, Any]:
    words = tokenize_words(text)
    total_words = len(words)
    if total_words == 0:
        return {"score": 0, "ttr": 0.0, "total_words": 0}

    distinct = len(set(words))
    ttr = distinct / total_words

    # Map TTR to bands
    if ttr >= 0.9:
        score = 100
    elif ttr >= 0.7:
        score = 80
    elif ttr >= 0.5:
        score = 60
    elif ttr >= 0.3:
        score = 40
    else:
        score = 20

    return {"score": score, "ttr": ttr, "total_words": total_words}

# ---------- CLARITY (FILLER WORD RATE) ---------- #

def clarity_score(text: str) -> Dict[str, Any]:
    words = tokenize_words(text)
    total_words = len(words) or 1
    t = clean_text(text)

    filler_count = 0
    for filler in FILLER_WORDS:
        if " " in filler:
            filler_count += t.count(filler)
        else:
            filler_count += words.count(filler)

    filler_rate = (filler_count / total_words) * 100

    if filler_rate <= 3:
        score = 100
    elif filler_rate <= 6:
        score = 80
    elif filler_rate <= 9:
        score = 60
    elif filler_rate <= 12:
        score = 40
    else:
        score = 20

    return {
        "score": score,
        "filler_count": filler_count,
        "filler_rate_percent": filler_rate
    }

# ---------- ENGAGEMENT (SIMPLE LEXICON-BASED) ---------- #

def engagement_score(text: str) -> Dict[str, Any]:
    words = tokenize_words(text)

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos_count + neg_count

    if total == 0:
        positive_prob = 0.5  # neutral if nothing matched
    else:
        positive_prob = pos_count / total

    # Convert to 0–100 rubric-like score
    if positive_prob >= 0.9:
        score = 100
    elif positive_prob >= 0.7:
        score = 80
    elif positive_prob >= 0.5:
        score = 60
    elif positive_prob >= 0.3:
        score = 40
    else:
        score = 20

    return {
        "score": score,
        "positive_prob": positive_prob,
        "pos_count": pos_count,
        "neg_count": neg_count
    }

# ---------- MAIN ENTRY POINT ---------- #

def rule_based_scores(text: str) -> Dict[str, Any]:
    word_count = len(tokenize_words(text))

    sal = detect_salutation(text)
    kw = detect_keywords(text)
    flow = basic_flow_check(text)
    sp = speech_rate_score(word_count)
    gr = grammar_score(text)
    vocab = vocabulary_score(text)
    clar = clarity_score(text)
    eng = engagement_score(text)

    return {
        "word_count": word_count,
        "Salutation": sal["score"],
        "Keyword Presence": kw["score"],
        "Flow": flow["score"],
        "Speech Rate": sp["score"],
        "Grammar": gr["score"],
        "Vocabulary": vocab["score"],
        "Clarity": clar["score"],
        "Engagement": eng["score"],
        "details": {
            "salutation": sal,
            "keywords": kw,
            "flow": flow,
            "speech_rate": sp,
            "grammar": gr,
            "vocabulary": vocab,
            "clarity": clar,
            "engagement": eng
        }
    }