import os
import sqlite3
import json
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from werkzeug.utils import secure_filename

from services.parser_service import parse_resume
from services.scoring_service import analyze_multiple_resumes
from services.report_service import build_report

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "resumes.db")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "resume-screening-secret-2024")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            resume_text TEXT,
            job_description TEXT,
            keyword_score REAL DEFAULT 0,
            skill_score REAL DEFAULT 0,
            tfidf_score REAL DEFAULT 0,
            ats_score REAL DEFAULT 0,
            overall_score REAL DEFAULT 0,
            matched_skills TEXT DEFAULT '[]',
            missing_skills TEXT DEFAULT '[]',
            matched_keywords TEXT DEFAULT '[]',
            missing_keywords TEXT DEFAULT '[]',
            recommendation TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_candidate(data, jd_text):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO candidates (
            filename, resume_text, job_description,
            keyword_score, skill_score, tfidf_score, ats_score, overall_score,
            matched_skills, missing_skills, matched_keywords, missing_keywords,
            recommendation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["filename"],
            data.get("resume_text", ""),
            jd_text,
            data.get("keyword_score", 0),
            data.get("skill_score", 0),
            data.get("tfidf_score", 0),
            data.get("ats_score", 0),
            data.get("overall_score", 0),
            json.dumps(data.get("matched_skills", [])),
            json.dumps(data.get("missing_skills", [])),
            json.dumps(data.get("matched_keywords", [])),
            json.dumps(data.get("missing_keywords", [])),
            data.get("recommendation", ""),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def get_candidate_by_id(candidate_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    record = dict(row)
    for field in ("matched_skills", "missing_skills", "matched_keywords", "missing_keywords"):
        try:
            record[field] = json.loads(record[field])
        except (json.JSONDecodeError, TypeError):
            record[field] = []
    return record


def get_all_candidates():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM candidates ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    candidates = []
    for row in rows:
        record = dict(row)
        for field in ("matched_skills", "missing_skills", "matched_keywords", "missing_keywords"):
            try:
                record[field] = json.loads(record[field])
            except (json.JSONDecodeError, TypeError):
                record[field] = []
        candidates.append(record)
    return candidates


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return filepath, filename


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    jd_text = request.form.get("job_description", "").strip()
    if not jd_text:
        flash("Please enter a job description.", "error")
        return redirect(url_for("upload"))

    files = request.files.getlist("resumes")
    if not files or all(f.filename == "" for f in files):
        flash("Please upload at least one resume.", "error")
        return redirect(url_for("upload"))

    resume_list = []
    errors = []

    for file in files:
        if file.filename == "":
            continue
        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: unsupported file type.")
            continue
        try:
            filepath, filename = save_upload(file)
            resume_text = parse_resume(filepath)
            resume_list.append((filename, resume_text))
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    for err in errors:
        flash(err, "warning")

    if not resume_list:
        flash("No resumes could be parsed. Please check your files.", "error")
        return redirect(url_for("upload"))

    results_df = analyze_multiple_resumes(resume_list, jd_text)

    # Persist results to database
    for _, row in results_df.iterrows():
        save_candidate(row.to_dict(), jd_text)

    flash(f"Analysis complete. {len(resume_list)} resume(s) processed.", "success")
    return redirect(url_for("results"))


@app.route("/results")
def results():
    candidates = get_all_candidates()
    # Group by the latest batch (same created_at minute)
    if candidates:
        latest_time = candidates[0]["created_at"][:16]  # YYYY-MM-DD HH:MM
        latest_batch = [c for c in candidates if c["created_at"][:16] == latest_time]
        latest_batch.sort(key=lambda x: x["overall_score"], reverse=True)
        for i, c in enumerate(latest_batch):
            c["rank"] = i + 1
        return render_template("results.html", candidates=latest_batch)
    flash("No results yet. Please upload and analyze resumes first.", "info")
    return redirect(url_for("upload"))


@app.route("/report/<int:candidate_id>")
def report(candidate_id):
    record = get_candidate_by_id(candidate_id)
    if record is None:
        flash("Report not found.", "error")
        return redirect(url_for("results"))
    report_data = build_report(record)
    return render_template("report.html", report=report_data, candidate_id=candidate_id)


@app.route("/history")
def history():
    candidates = get_all_candidates()
    return render_template("history.html", candidates=candidates)


@app.route("/clear-history", methods=["POST"])
def clear_history():
    conn = get_db()
    conn.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()
    flash("Screening history cleared.", "success")
    return redirect(url_for("history"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
