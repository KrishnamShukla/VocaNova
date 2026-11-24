# VocaNova AI — Career Discovery Portal

A Flask-based career recommendation website built around the VocaNova weighted profile-matching project.

## Features
- Dashboard with assessment activity and quick actions
- Six-section student profile assessment
- Personalized top career matches with weighted scores
- Career library with search and interest filters
- Individual career pages with degrees, skills and career pathways
- Saved assessment history stored locally in `assessments.json`
- About page explaining the matching model and category weights

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Start the app:
   `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

Assessment history is stored on the computer running the app. The recommendation engine uses predefined career profiles and weighted profile matching; it is not a trained machine-learning model.
