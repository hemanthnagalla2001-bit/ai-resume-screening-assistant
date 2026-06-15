from models.resume_scorer import generate_ats_suggestions


def build_report(candidate_record):
    matched_keywords = candidate_record.get("matched_keywords", [])
    missing_keywords = candidate_record.get("missing_keywords", [])
    matched_skills = candidate_record.get("matched_skills", [])
    missing_skills = candidate_record.get("missing_skills", [])
    resume_text = candidate_record.get("resume_text", "")

    suggestions = generate_ats_suggestions(
        resume_text,
        matched_keywords,
        missing_keywords,
        matched_skills,
        missing_skills,
    )

    strengths = []
    if candidate_record.get("keyword_score", 0) >= 60:
        strengths.append("Strong keyword alignment with the job description.")
    if candidate_record.get("skill_score", 0) >= 60:
        strengths.append("Good coverage of required technical skills.")
    if candidate_record.get("tfidf_score", 0) >= 60:
        strengths.append("High content similarity to the job description.")
    if candidate_record.get("ats_score", 0) >= 60:
        strengths.append("Resume is well-structured for ATS parsing.")
    if not strengths:
        strengths.append("Some relevant terms were identified in the resume.")

    return {
        "filename": candidate_record.get("filename", "Unknown"),
        "overall_score": candidate_record.get("overall_score", 0),
        "keyword_score": candidate_record.get("keyword_score", 0),
        "skill_score": candidate_record.get("skill_score", 0),
        "tfidf_score": candidate_record.get("tfidf_score", 0),
        "ats_score": candidate_record.get("ats_score", 0),
        "recommendation": candidate_record.get("recommendation", "N/A"),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions,
        "strengths": strengths,
    }
