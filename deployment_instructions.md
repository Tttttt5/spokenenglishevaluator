Deployment / Local Server Instructions

This document explains how to deploy and run the Spoken English Evaluator application on a local machine.
The tool contains:
- Backend (FastAPI + Python)
- Frontend (HTML/CSS/JS)
- Rubric folder with Excel file

1. Prerequisites:
- Python 3.9+
- Git (optional)
- Web browser

2. Download or Clone the Project:
Option A:
git clone https://github.com/Tttttt5

Option B:
Download ZIP from GitHub → Extract → Open folder.

3. Create and Activate Virtual Environment:
python -m venv venv

Windows:
venv\Scripts\activate


4. Install Dependencies:
pip install -r requirements.txt

5. Run Backend:
uvicorn backend.app:app --reload --port 8000

Open:
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs

6. Run Frontend:
Open frontend/index.html in your browser.
Paste transcript → Click Score.

7. Stop Server:
Ctrl + C
deactivate

8. Optional Deployment:
Render for backend
GitHub Pages for frontend

9. Troubleshooting:
Ensure backend is running
Check script.js API URL
Install missing modules

10. Project Structure:
backend/
frontend/
rubric/
requirements.txt
README.md
deployment_instructions.md
