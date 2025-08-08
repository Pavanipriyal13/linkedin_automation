from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import resume_matcher.parser as parser

def compute_match_score(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)

def match_resume(resume_path, job_description):
    resume_text = parser.extract_text(resume_path)
    return compute_match_score(resume_text, job_description)
