import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "swift",
    "kotlin", "php", "scala", "r", "matlab", "sql", "nosql", "html", "css",
    "react", "angular", "vue", "node", "express", "django", "flask", "fastapi", "spring",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "bash",
    "machine learning", "deep learning", "nlp", "computer vision", "data science",
    "api", "rest", "graphql", "microservices", "devops", "ci/cd", "agile", "scrum",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "tableau", "power bi", "spark", "hadoop", "airflow",
    "communication", "leadership", "teamwork", "problem solving", "analytical",
]


def extract_keywords_from_jd(jd_text):
    text = jd_text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.add(skill)
    words = re.findall(r'\b[a-z][a-z0-9+#.]{1,20}\b', text)
    stop_words = {
        "the", "and", "for", "are", "with", "that", "this", "from", "have",
        "will", "you", "your", "our", "they", "their", "must", "able", "also",
        "experience", "years", "strong", "good", "knowledge", "work", "team",
        "ability", "skills", "required", "including", "such", "may", "not",
        "should", "well", "both", "each", "more", "than", "into",
    }
    custom_keywords = {w for w in words if w not in stop_words and len(w) > 2}
    return list(found | custom_keywords)


def compute_keyword_score(resume_text, keywords):
    if not keywords:
        return 0.0
    text = resume_text.lower()
    matched = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text)]
    return round(len(matched) / len(keywords) * 100, 2)


def compute_skill_score(resume_text, jd_text):
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    jd_skills = [s for s in SKILL_KEYWORDS if re.search(r'\b' + re.escape(s) + r'\b', jd_lower)]
    if not jd_skills:
        return 0.0, [], []
    matched = [s for s in jd_skills if re.search(r'\b' + re.escape(s) + r'\b', resume_lower)]
    missing = [s for s in jd_skills if s not in matched]
    score = round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 0.0
    return score, matched, missing


def compute_tfidf_similarity(resume_text, jd_text):
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        corpus = [jd_text, resume_text]
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    except Exception:
        return 0.0


def compute_ats_score(resume_text, keywords):
    score = 0.0

    # Keyword density check
    kw_score = compute_keyword_score(resume_text, keywords)
    score += kw_score * 0.5

    # Section presence check
    text_lower = resume_text.lower()
    sections = ["experience", "education", "skills", "summary", "objective"]
    section_hits = sum(1 for s in sections if s in text_lower)
    score += (section_hits / len(sections)) * 30

    # Length check: resumes should be substantive
    word_count = len(resume_text.split())
    if word_count >= 300:
        score += 20
    elif word_count >= 150:
        score += 10

    return min(round(score, 2), 100.0)


def compute_overall_score(keyword_score, skill_score, tfidf_score, ats_score):
    overall = (
        keyword_score * 0.30 +
        skill_score * 0.30 +
        tfidf_score * 0.25 +
        ats_score * 0.15
    )
    return round(overall, 2)


def get_recommendation(overall_score):
    if overall_score >= 75:
        return "Strong Match"
    elif overall_score >= 55:
        return "Good Match"
    elif overall_score >= 35:
        return "Moderate Match"
    else:
        return "Low Match"


def score_resume(resume_text, jd_text):
    keywords = extract_keywords_from_jd(jd_text)
    keyword_score = compute_keyword_score(resume_text, keywords)
    skill_score, matched_skills, missing_skills = compute_skill_score(resume_text, jd_text)
    tfidf_score = compute_tfidf_similarity(resume_text, jd_text)
    ats_score = compute_ats_score(resume_text, keywords)
    overall_score = compute_overall_score(keyword_score, skill_score, tfidf_score, ats_score)
    recommendation = get_recommendation(overall_score)

    matched_kw = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', resume_text.lower())]
    missing_kw = [kw for kw in keywords if kw not in matched_kw]

    return {
        "keyword_score": keyword_score,
        "skill_score": skill_score,
        "tfidf_score": tfidf_score,
        "ats_score": ats_score,
        "overall_score": overall_score,
        "recommendation": recommendation,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_kw[:30],
        "missing_keywords": missing_kw[:30],
    }


def rank_candidates(candidates_df):
    return candidates_df.sort_values("overall_score", ascending=False).reset_index(drop=True)


def generate_ats_suggestions(resume_text, matched_keywords, missing_keywords, matched_skills, missing_skills):
    suggestions = []
    text_lower = resume_text.lower()

    if "summary" not in text_lower and "objective" not in text_lower:
        suggestions.append("Add a professional summary or objective section.")
    if "experience" not in text_lower:
        suggestions.append("Include a dedicated Work Experience section.")
    if "education" not in text_lower:
        suggestions.append("Add an Education section with degrees and institutions.")
    if "skills" not in text_lower:
        suggestions.append("Add a Skills section listing your technical and soft skills.")
    if len(resume_text.split()) < 300:
        suggestions.append("Expand your resume — aim for at least 300 words for better ATS parsing.")
    if missing_keywords:
        suggestions.append(f"Include missing keywords: {', '.join(missing_keywords[:10])}.")
    if missing_skills:
        suggestions.append(f"Highlight or acquire skills: {', '.join(missing_skills[:8])}.")
    if not suggestions:
        suggestions.append("Resume structure looks solid. Focus on quantifying achievements.")

    return suggestions
