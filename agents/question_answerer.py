def generate_answers(question_text: str, resume_text: str) -> str:
    prompt = f"""
You are a job applicant. Answer the following question professionally and concisely based on your resume.

--- Question ---
{question_text}

--- Resume ---
{resume_text}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
