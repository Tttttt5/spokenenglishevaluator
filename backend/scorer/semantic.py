from typing import Dict, Any

from sentence_transformers import SentenceTransformer, util

# Load model once at import time
# Small, fast model suitable for semantic similarity
model = SentenceTransformer("all-MiniLM-L6-v2")

# Short descriptions for each rubric metric
SEMANTIC_RUBRIC_DESCRIPTIONS = {
    "Salutation": (
        "A polite greeting at the beginning of the self introduction, such as "
        "good morning, hello everyone, I am excited to introduce myself."
    ),
    "Keyword Presence": (
        "The introduction should mention key personal details like name, age, "
        "class or school, family, hobbies or interests, and optional goals or strengths."
    ),
    "Flow": (
        "The introduction should follow a logical structure: greeting, name, basic details, "
        "additional details such as hobbies and goals, and a brief closing."
    ),
    "Speech Rate": (
        "The text should sound like a natural short spoken introduction, not unnaturally "
        "rushed or extremely slow when read aloud."
    ),
    "Grammar": (
        "The sentences should be grammatically correct, with proper word order and basic "
        "tenses used accurately in English."
    ),
    "Vocabulary": (
        "The introduction should use a reasonable variety of words and some descriptive "
        "vocabulary instead of repeating the same simple words."
    ),
    "Clarity": (
        "The introduction should be clear and easy to follow, without too many filler phrases "
        "such as um, like, you know."
    ),
    "Engagement": (
        "The tone should sound positive, interested and confident, showing enthusiasm about "
        "oneself, hobbies and future goals."
    ),
}


def semantic_scores(text: str) -> Dict[str, Any]:
    """
    Compute semantic similarity between the full transcript and each metric description.
    Returns scores in 0–100 per metric.
    """
    text_embedding = model.encode(text, convert_to_tensor=True)

    scores: Dict[str, float] = {}
    raw_similarities: Dict[str, float] = {}

    for metric, desc in SEMANTIC_RUBRIC_DESCRIPTIONS.items():
        desc_embedding = model.encode(desc, convert_to_tensor=True)
        sim = util.cos_sim(text_embedding, desc_embedding).item()  # usually 0–1 range

        # Normalize similarity from [-1,1] to [0,1], then scale to 0–100
        normalized = max(0.0, min((sim + 1.0) / 2.0, 1.0))
        score = normalized * 100.0

        scores[metric] = score
        raw_similarities[metric] = sim

    return {
        "scores": scores,
        "raw_similarities": raw_similarities,
        "descriptions": SEMANTIC_RUBRIC_DESCRIPTIONS,
    }