# Spoken English Evaluator – Rubric-based Self-introduction Scorer

This project is a web app + API that evaluates students' **spoken English self-introductions** (transcripts) using a **rubric-based scoring system**.

It takes a **transcript** (text) of a short self-introduction and outputs:

- Overall score (0–100)
- Per-criterion scores (Content & Structure, Speech Rate, Grammar, Vocabulary, Clarity, Engagement)
- Rule-based vs semantic scores
- Per-criterion feedback

The rubric and sample transcripts are based on the Excel file provided in the case study:  
`rubric/Case study for interns.xlsx`.

---

## How this maps to the case study requirements

**1. Accept transcript text (UI text area / text file)**  
- The **frontend** (`frontend/index.html`) has a textarea for the transcript and a **Score** button.
- It sends the text to the backend API `/score`.

**2. Compute per-criterion scores using the rubric**  
- The rubric fields (criteria, keywords, weight, band ranges) are manually encoded in:
  - `backend/scorer/rule_based.py` (keywords, salutation, filler list, bands)
  - `backend/scorer/semantic.py` (short descriptions per criterion)
- Rubric weights:
  - Salutation – 5
  - Keyword Presence – 30
  - Flow – 5
  - Speech Rate – 10
  - Grammar – 10
  - Vocabulary – 10
  - Clarity – 15
  - Engagement – 15  
  (Sum = 100)

**3. Uses three approaches combined**

- **Rule-based** (in `rule_based.py`):
  - Keyword presence for must-have and good-to-have fields
  - Salutation detection based on greeting phrases
  - Flow check (greeting → name/basic details → extras)
  - Approximate speech rate via word count
  - Heuristic grammar scoring (sentence length, “and” overuse)
  - Vocabulary richness via TTR (Type-Token Ratio)
  - Clarity via filler word rate
  - Engagement via a simple sentiment lexicon

- **NLP-based semantic similarity** (in `semantic.py`):
  - Uses `sentence-transformers` (`all-MiniLM-L6-v2`)
  - Each rubric criterion has a short description text
  - The transcript is embedded; cosine similarity is computed with each description
  - Similarity is normalized and scaled to a semantic score 0–100

- **Data/rubric-driven weighting** (in `app.py`):
  - For each metric:
    - `combined_score = 0.6 * rule_score + 0.4 * semantic_score`
  - Each metric has a rubric weight (e.g., Keyword Presence = 30)
  - Final score is the sum of `combined_score * (weight / 100)` across all metrics  
    → Normalized overall score between 0 and 100

**4. Detailed output**

The `/score` API returns:

- `overall_score` – final score (0–100)
- `word_count` – number of words in transcript
- `criteria` – array, one per criterion, with:
  - `criterion` – name (e.g., "Keyword Presence")
  - `score` – combined score (rule + semantic)
  - `rule_score` – raw rule-based score
  - `semantic_score` – semantic similarity score
  - `weight` – rubric weight
  - `details` – extra info (keywords found, filler rate, etc.)
  - `feedback` – short textual feedback

The **frontend** displays:
- Overall score + word count
- A bar chart (Chart.js) of per-criterion scores
- Detailed cards with scores and feedback for each criterion

**5. Simple frontend web UI (paste & click Score)**  
- Implemented in:
  - `frontend/index.html`
  - `frontend/styles.css`
  - `frontend/script.js`
- No framework needed; pure HTML/CSS/JS + Chart.js via CDN.

**6. Deployed (GitHub + local run, optional cloud)**  
- GitHub repo contains:
  - Source code
  - `requirements.txt`
  - `README.md` with scoring formula and run instructions
  - `deployment_instructions.md` with local deployment steps  
- Backend is designed to run locally using Uvicorn.  
- The app can be deployed on any free tier (Render / Railway / PythonAnywhere) and the frontend can be hosted via GitHub Pages if desired.

---

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, Sentence-Transformers
- **Frontend**: HTML, CSS, Vanilla JavaScript, Chart.js
- **Rubric**: Excel file from case study (manually encoded into constants)

---

## Project Structure

```text
backend/
  app.py                 # FastAPI app and /score endpoint
  __init__.py
  scorer/
    __init__.py
    rule_based.py        # rule-based scoring logic
    semantic.py          # semantic similarity scoring

frontend/
  index.html             # UI (textarea + results)
  styles.css             # layout and styling
  script.js              # calls backend and renders chart/cards

rubric/
  Case study for interns.xlsx

requirements.txt
README.md
deployment_instructions.md
.gitignore