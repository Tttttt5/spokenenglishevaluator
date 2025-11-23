from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


try:
    from backend.scorer.rule_based import rule_based_scores
    from backend.scorer.semantic import semantic_scores
except ModuleNotFoundError:
    from scorer.rule_based import rule_based_scores
    from scorer.semantic import semantic_scores



app = FastAPI(title="Spoken English Scorer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for dev; tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptInput(BaseModel):
    text: str

# Weights from rubric (sum = 100)
WEIGHTS = {
    "Salutation": 5,
    "Keyword Presence": 30,
    "Flow": 5,
    "Speech Rate": 10,
    "Grammar": 10,
    "Vocabulary": 10,
    "Clarity": 15,
    "Engagement": 15,
}

@app.get("/")
def read_root():
    return {"message": "Spoken English Scorer API is running"}



def feedback_for(metric: str, score: float, details: dict) -> str:
    if metric == "Salutation":
        level = details.get("level")
        if score == 0:
            return (
                "No clear greeting detected. Start with a polite salutation like "
                "'Good morning' or 'Hello everyone'."
            )
        elif score < 70:
            return (
                f"Greeting detected ({level}). You can make it warmer or more "
                "enthusiastic, e.g. 'I am excited to introduce myself today.'"
            )
        else:
            return f"Nice greeting ({level}). Your opening sounds polite and appropriate."

    if metric == "Keyword Presence":
        must_found = details.get("must_have_found", [])
        good_found = details.get("good_to_have_found", [])
        return (
            "You covered some key details about yourself. "
            "Try to clearly mention name, age, class/school, family, and hobbies. "
            "Optional details like goals, where you are from, strengths, or a fun fact "
            "make the introduction richer. "
            f"(Found must-have keywords: {', '.join(must_found) or 'none'}; "
            f"good-to-have: {', '.join(good_found) or 'none'}.)"
        )

    if metric == "Flow":
        if details.get("order_ok"):
            return "Your introduction follows a logical order and is easy to follow."
        else:
            return (
                "The information jumps around a bit. Try this structure: "
                "greeting → name → basic details (age, class, school, place) → "
                "extra details (hobbies, goals, fun fact) → closing."
            )

    if metric == "Speech Rate":
        band = details.get("band")
        if band in ["Too fast", "Fast"]:
            return (
                "You may be speaking too quickly. Slow down slightly and add small "
                "pauses so each sentence is clear."
            )
        elif band in ["Too slow"]:
            return (
                "You might be speaking a bit slowly. Try connecting phrases more "
                "smoothly to sound more natural."
            )
        else:
            return "Your speaking pace seems comfortable for a short introduction."

    if metric == "Grammar":
        if score > 85:
            return (
                "Sentence structure looks quite good for a short intro. "
                "Keep using clear, simple sentences."
            )
        elif score > 60:
            return (
                "Some sentences may be long or linked with many 'and's. "
                "Try breaking long sentences into two and avoid chaining too many ideas "
                "with 'and'."
            )
        else:
            return (
                "Sentences may be too long or loosely connected. "
                "Use shorter sentences with clear full stops, and avoid using 'and' "
                "too often in a single sentence."
            )

    if metric == "Vocabulary":
        if score > 85:
            return (
                "Good variety of words. You are using diverse vocabulary for a short "
                "introduction."
            )
        elif score > 60:
            return (
                "Vocabulary is okay, but you repeat some words. Try using a few "
                "different adjectives and verbs to describe yourself and your hobbies."
            )
        else:
            return (
                "You rely on very simple, repeated words. Learn and use some new words "
                "to talk about your interests, strengths, and goals."
            )

    if metric == "Clarity":
        filler_rate = details.get("filler_rate_percent", 0)
        if score > 85:
            return "Very few filler words. Your speech is clear and to the point."
        elif score > 60:
            return (
                f"You use some fillers (around {filler_rate:.1f}% of your words). "
                "Try replacing 'um/like' with short pauses."
            )
        else:
            return (
                f"Many filler words detected (around {filler_rate:.1f}% of your words). "
                "Practice speaking slower and pausing instead of saying 'um' or 'like'."
            )

    if metric == "Engagement":
        if score > 85:
            return (
                "Your tone feels positive and engaged. You sound interested and "
                "confident while speaking about yourself."
            )
        elif score > 60:
            return (
                "Tone is mostly neutral with some positivity. "
                "Try adding a bit more energy or warmth when you talk about your hobbies "
                "or goals."
            )
        else:
            return (
                "Tone may sound a little flat or less positive. "
                "Try to sound more enthusiastic when you introduce yourself, especially "
                "when talking about your interests and dreams."
            )

    return "No specific feedback available for this criterion."



@app.post("/score")
def score_transcript(payload: TranscriptInput):
    text = payload.text

    # Rule-based scores
    rb = rule_based_scores(text)
    word_count = rb["word_count"]
    rb_details = rb["details"]

    # Semantic scores
    sem = semantic_scores(text)
    sem_scores = sem["scores"]

    weighted_sum = 0.0
    criteria_output = []

    metrics_in_order = [
        "Salutation",
        "Keyword Presence",
        "Flow",
        "Speech Rate",
        "Grammar",
        "Vocabulary",
        "Clarity",
        "Engagement",
    ]

    detail_key_map = {
        "Salutation": "salutation",
        "Keyword Presence": "keywords",
        "Flow": "flow",
        "Speech Rate": "speech_rate",
        "Grammar": "grammar",
        "Vocabulary": "vocabulary",
        "Clarity": "clarity",
        "Engagement": "engagement",
    }

    for metric in metrics_in_order:
        rule_score = rb.get(metric, 0.0)
        semantic_score = sem_scores.get(metric, 0.0)

        # 60% rule-based, 40% semantic
        combined_score = 0.6 * rule_score + 0.4 * semantic_score

        weight = WEIGHTS[metric]
        metric_details = rb_details.get(detail_key_map[metric], {})

        weighted_sum += combined_score * (weight / 100.0)

        criteria_output.append(
            {
                "criterion": metric,
                "score": combined_score,
                "rule_score": rule_score,
                "semantic_score": semantic_score,
                "weight": weight,
                "details": metric_details,
                "feedback": feedback_for(metric, combined_score, metric_details),
            }
        )

    overall_score = weighted_sum  # already 0–100

    return {
        "overall_score": overall_score,
        "word_count": word_count,
        "criteria": criteria_output,
    }
