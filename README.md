# Resume Screening Assistant

An intelligent recruitment web application that evaluates resumes against job descriptions using automated scoring, candidate ranking, ATS compatibility reports, and skill-gap analysis.

---

## Features

- **Resume Upload** — Upload multiple resumes in PDF, DOCX, or TXT format at once
- **Job Description Processing** — Automatically extracts required skills, keywords, and qualifications
- **Automated Scoring** — Four-dimensional scoring: keyword match, skill relevance, TF-IDF similarity, ATS compatibility
- **Candidate Ranking** — Ranks all candidates from strongest to weakest match with a recommendation label
- **ATS Compatibility Report** — Per-candidate report with formatting suggestions, matched/missing keywords, and skill gaps
- **Screening History** — All results stored in SQLite; view and clear history anytime

---

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Backend  | Python 3.10+, Flask 3.0                        |
| ML/Data  | scikit-learn (TF-IDF, cosine similarity), Pandas |
| Parsing  | pdfplumber (PDF), python-docx (DOCX)            |
| Database | SQLite (via Python's built-in `sqlite3`)        |
| Frontend | HTML5, CSS3, Vanilla JavaScript                 |

---

## Folder Structure

```
ai-resume-screening-assistant/
├── app.py                  # Flask application and routes
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── database/
│   └── resumes.db          # SQLite database (auto-created on first run)
├── models/
│   └── resume_scorer.py    # Scoring algorithms
├── services/
│   ├── parser_service.py   # Resume text extraction
│   ├── scoring_service.py  # Orchestrates scoring pipeline
│   └── report_service.py   # ATS report generation
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── results.html
│   ├── report.html
│   └── history.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── uploads/
    └── .gitkeep
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-resume-screening-assistant
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The app will start at `http://localhost:5000`.

---

## How to Use

1. Open `http://localhost:5000` in your browser.
2. Click **Upload** in the navigation bar.
3. Upload one or more resumes (PDF, DOCX, or TXT).
4. Paste the job description into the text area.
5. Click **Analyze Resumes**.
6. View the ranked results table.
7. Click **View Report** on any candidate for a detailed ATS report.

---

## Database Details

The SQLite database is created automatically at `database/resumes.db` on first startup. The `candidates` table stores:

| Column           | Type    | Description                        |
|------------------|---------|------------------------------------|
| `id`             | INTEGER | Primary key                        |
| `filename`       | TEXT    | Uploaded resume file name          |
| `resume_text`    | TEXT    | Extracted and cleaned resume text  |
| `job_description`| TEXT    | Job description used for scoring   |
| `keyword_score`  | REAL    | Keyword match score (0–100)        |
| `skill_score`    | REAL    | Skill relevance score (0–100)      |
| `tfidf_score`    | REAL    | TF-IDF cosine similarity (0–100)   |
| `ats_score`      | REAL    | ATS compatibility score (0–100)    |
| `overall_score`  | REAL    | Weighted overall score (0–100)     |
| `matched_skills` | TEXT    | JSON array of matched skills       |
| `missing_skills` | TEXT    | JSON array of missing skills       |
| `matched_keywords`| TEXT   | JSON array of matched keywords     |
| `missing_keywords`| TEXT   | JSON array of missing keywords     |
| `recommendation` | TEXT    | Match recommendation label         |
| `created_at`     | TEXT    | UTC timestamp                      |

---

## Scoring Methodology

Each resume is evaluated on four dimensions:

| Dimension          | Weight | Description                                                    |
|--------------------|--------|----------------------------------------------------------------|
| Keyword Match      | 30%    | Fraction of JD-extracted keywords found in the resume         |
| Skill Relevance    | 30%    | Fraction of required technical skills present in the resume   |
| TF-IDF Similarity  | 25%    | Cosine similarity between JD and resume using TF-IDF vectors  |
| ATS Compatibility  | 15%    | Structural score based on sections, length, and keyword density|

**Recommendation thresholds:**

| Label           | Overall Score |
|-----------------|---------------|
| Strong Match    | ≥ 75%         |
| Good Match      | ≥ 55%         |
| Moderate Match  | ≥ 35%         |
| Low Match       | < 35%         |

---

## Screenshots

_Add screenshots of the Home, Upload, Results, and Report pages here._

---

## Future Improvements

- Export ranked results to CSV or PDF
- Email notifications for top-ranked candidates
- Resume anonymization for bias-free screening
- Support for additional file formats (RTF, ODT)
- Integration with ATS platforms (Greenhouse, Lever)
- Candidate comparison side-by-side view
- User authentication and multi-job session management
