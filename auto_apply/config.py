import os
from dotenv import load_dotenv

# Load environment variables from a .env if present (project root or cwd)
load_dotenv()


class Config:
    def __init__(self):
        # Prefer the resume in resume_matcher by default; allow override via env
        default_resume = os.path.abspath(
            "resume_matcher/PavaniPriyalDharnamoniResume.pdf"
        )
        self.RESUME_PATH = os.environ.get("RESUME_PATH", default_resume)

        # Credentials
        self.USERNAME = os.environ.get("LINKEDIN_EMAIL")
        self.PASSWORD = os.environ.get("LINKEDIN_PASSWORD")


CONFIG = Config()

