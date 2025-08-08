from resume_matcher.matcher import match_resume

resume_path = "resume_matcher/PavaniPriyalDharnamoniResume.pdf"

job_description = """
We are looking for a Python Developer with experience in web scraping, APIs, and automation tools.
Familiarity with Flask, Selenium, and LinkedIn APIs is a plus.
"""

score = match_resume(resume_path, job_description)
print(f"Resume matches the job description with a score of {score}%")


