from models.resume_scorer import score_resume, rank_candidates
import pandas as pd


def analyze_resume(resume_text, jd_text, filename):
    result = score_resume(resume_text, jd_text)
    result["filename"] = filename
    result["resume_text"] = resume_text
    result["jd_text"] = jd_text
    return result


def analyze_multiple_resumes(resume_list, jd_text):
    """
    resume_list: list of (filename, resume_text) tuples
    Returns sorted DataFrame of results.
    """
    records = []
    for filename, resume_text in resume_list:
        try:
            result = analyze_resume(resume_text, jd_text, filename)
            records.append(result)
        except Exception as e:
            records.append({
                "filename": filename,
                "keyword_score": 0,
                "skill_score": 0,
                "tfidf_score": 0,
                "ats_score": 0,
                "overall_score": 0,
                "recommendation": "Parse Error",
                "matched_skills": [],
                "missing_skills": [],
                "matched_keywords": [],
                "missing_keywords": [],
                "resume_text": "",
                "jd_text": jd_text,
                "error": str(e),
            })

    df = pd.DataFrame(records)
    return rank_candidates(df)
