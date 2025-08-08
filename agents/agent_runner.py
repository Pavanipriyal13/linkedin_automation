import google.generativeai as genai
import os

# Configure Gemini model lazily to avoid failing at import time
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
model = None
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-pro")

def ask_agent_if_should_apply(title, company, description, resume_text):
    prompt = f"""
    Job Title: {title}
    Company: {company}
    Job Description: {description}

    Candidate Resume:
    {resume_text}

    Based on the resume and job description, should the candidate apply to this position?
    Respond with only "yes" or "no" and a short reason.
    """
    if model is None:
        return "no"  # fail-safe default
    response = model.generate_content(prompt)
    return response.text.strip().lower()

def answer_application_questions(question, resume_text):
    prompt = f"""
    Candidate Resume:
    {resume_text}

    Answer the following application question based on the resume:

    Q: {question}

    A:"""
    if model is None:
        return ""
    response = model.generate_content(prompt)
    return response.text.strip()
