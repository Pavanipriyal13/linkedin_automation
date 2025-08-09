## linkedin_automation

An async Playwright-powered LinkedIn auto-apply bot focused on AI/ML internships. It scrapes relevant roles from LinkedIn search, filters them with a Gemini (Google AI) agent, and automatically applies to the ones that are a good fit — attaching your resume and answering application questions when possible.

Use responsibly and at your own risk. Automating third‑party sites may violate their Terms of Service.

### What this project does
- **Scrapes AI Engineering and AI-related internships** from LinkedIn search using `job_monitor/monitor.py`.
- **Provides SQLite persistence** via `database/db.py` (helpers to store and track jobs). The current CLI writes a JSON cache for the auto-apply step; DB wiring is recommended and example code is provided below.
- **Evaluates relevance with a Gemini agent** (`agents/agent_runner.py`) using your resume and the job context.
- **Auto-applies to relevant internships** with `auto_apply/apply.py`, attaching your resume and answering common application questions.
- **Logs every viewed job** to `viewed_jobs.log` for transparency and optionally records successful applications to `applied_jobs.log`.
- **Async/await everywhere** for non-blocking browser automation.
- **Playwright** drives the browser; supports session reuse via `auth.json`.
- **.gitignore-friendly** workflow to keep secrets, virtualenvs, and local DB/logs out of Git.


### How it works (high-level workflow)
1) Configure keywords and location in `job_monitor/job_config.py`.
2) Run the job monitor to scrape listings from LinkedIn’s search page.
   - Jobs are saved to SQLite (source of truth) and also to `job_monitor/job_data.json` (temporary cache for the current auto-apply flow).
3) Each job can be scored by the Gemini agent for relevance vs your resume.
4) Run the auto-apply step to open each job, click Easy/Quick Apply, upload your resume, and answer common questions.
5) `viewed_jobs.log` and `applied_jobs.log` capture what happened for auditing.


### Repository structure
```text
.
├── agents/
│   ├── agent_runner.py       # Gemini prompts to decide if you should apply; answers form questions
│   └── question_answerer.py  # (Auxiliary) answer generation helper
├── auto_apply/
│   ├── apply.py              # Main auto-apply flow (async Playwright)
│   ├── autofill.py           # Logic to fill application forms
│   ├── browser.py            # Browser/context launcher with session reuse (auth.json)
│   ├── config.py             # Reads LINKEDIN_EMAIL/PASSWORD, RESUME_PATH
│   └── resume_uploader.py    # Uploads resume to application forms
├── database/
│   └── db.py                 # SQLite helpers: init, insert_job, get_pending_jobs, mark_job_as_applied
├── job_monitor/
│   ├── job_config.py         # Search keywords, location, filters
│   ├── monitor.py            # Scrapes LinkedIn search results (async Playwright)
│   └── job_data.json         # JSON cache of scraped jobs (legacy/temporary)
├── resume_matcher/           # Resume parsing/matching utilities (optional helpers)
├── main.py                   # Orchestrates auto-apply using JSON cache (see notes below)
├── config.py                 # Project-level config (RESUME_PATH, env loading)
├── requirements.txt          # Python dependencies
├── auth.json                 # Playwright storage state (created at runtime)
└── README.md
```


### Prerequisites
- Python 3.10+
- A LinkedIn account and credentials you control
- Playwright browsers installed


### Installation and setup
1) Create and activate a virtual environment, then install dependencies and Playwright browsers.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

2) Create a `.env` with required secrets. You can put this at the project root.

```ini
# .env
LINKEDIN_EMAIL=you@example.com
LINKEDIN_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key

# Optional
RESUME_PATH=/absolute/path/to/YourResume.pdf
```

Notes:
- `GOOGLE_API_KEY` is required for Gemini-based relevance scoring and question answering.
- `RESUME_PATH` defaults to `resume_matcher/PavaniPriyalDharnamoniResume.pdf` if not set.

3) First-time login and session reuse (auth.json)
- The auto-apply flow saves a Playwright storage state to `auth.json` after login so subsequent runs can reuse the session.
- If the file is missing or expires, the script will prompt you to log in again in the headful browser window.

4) Initialize the local database (optional)
- The monitor will create/populate the SQLite DB as needed; you can also import and call `database.db.init_db()` manually if desired.


### Configure your job search
Edit `job_monitor/job_config.py`:

```python
job_search_config = {
    "keywords": ["AI Intern", "Machine Learning Intern", "Data Science Intern"],
    "location": "India",
    "experience_level": ["Internship", "Entry level"],
    "remote": True,
    "posted_within_days": 1,
}
```


### Run: scrape jobs
This opens a headful Chromium window, signs in, runs the search, and scrapes listings.

```bash
python job_monitor/monitor.py
```

Outputs:
- Writes a JSON cache to `job_monitor/job_data.json` for the current auto-apply CLI.
- Prints found jobs to the terminal.
- Optional: persist to SQLite using `database/db.py` (see below).


### Run: auto-apply to relevant internships
The current CLI reads from the JSON cache and applies to each job link. The browser is headful so you can see and resolve challenges if needed.

```bash
python main.py
```

Behavior:
- Logs every viewed job to `viewed_jobs.log`.
- Logs successful applications to `applied_jobs.log` (best-effort).
- Reuses `auth.json` when available; otherwise prompts you to log in.

Relevance filtering with Gemini:
- `agents/agent_runner.py` contains `ask_agent_if_should_apply(...)`. Integrations can call this function with the job title/company/description and your resume text to decide whether to proceed. Ensure `GOOGLE_API_KEY` is set in your environment to enable Gemini.


### Optional: persist scraped jobs to SQLite
You can store each scraped job in SQLite and later drive the auto-apply from the DB instead of the JSON cache. Example integration inside `job_monitor/monitor.py` after you build each job dict:

```python
from database.db import init_db, insert_job

init_db()  # call once at startup
for job in jobs:
    insert_job(job["title"], job["url"], job["company"])  # persist
```

Later, read pending jobs in your apply step:

```python
from database.db import get_pending_jobs, mark_job_as_applied

for job_id, title, link, company in get_pending_jobs():
    result = await auto_apply_to_job(page, link)
    if result == "ok":
        mark_job_as_applied(job_id)
```


### Environment variables summary
- `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`: Used for LinkedIn login.
- `GOOGLE_API_KEY`: Enables Gemini model calls for relevance scoring and question answering.
- `RESUME_PATH` (optional): Absolute path to your PDF resume.


### .gitignore recommendations
Add a `.gitignore` to avoid committing secrets and machine-local artifacts:

```gitignore
# Python
.venv/
__pycache__/
*.pyc

# Playwright/State
auth.json

# Databases & logs
*.db
*.sqlite
*.log
viewed_jobs.log
applied_jobs.log

# Environment & IDE
.env
.env.*
.DS_Store
.idea/
.vscode/
```


### Known issues and limitations
- LinkedIn frequently changes UI and anti-bot mechanisms; selectors or flows may break and need updating.
- 2FA/CAPTCHA and checkpoint pages can interrupt login. Because the browser is headful, you can complete challenges manually and continue.
- Easy Apply coverage varies by posting. The script tries multiple selectors but some flows (multi-step uploads, custom portals) may be unsupported.
- Database helpers exist but the default CLI reads from the JSON cache. Wire DB calls as shown above if you prefer DB-first.
- Use of automation may violate LinkedIn’s Terms of Service; accounts can be rate-limited or restricted.


### Future improvements
- Wire auto-apply to read directly from the SQLite DB (`database/db.py`) and track application status with `mark_job_as_applied`.
- Add richer Gemini-based ranking/scoring using full job descriptions scraped per posting.
- Headless mode with robust checkpoint handling and retries.
- Dockerfile and containerized Playwright runtime.
- GitHub Actions workflow to run the monitor daily and notify via email/Slack.


### Troubleshooting
- Ensure both the Python package and browsers are installed: `pip install playwright` and `python -m playwright install chromium`.
- If login loops, delete `auth.json`, re-run and complete any MFA/captcha in the opened window.
- If selectors fail, inspect the page (DevTools) and update selectors in `job_monitor/monitor.py` and/or `auto_apply/apply.py`.
- Make sure environment variables are loaded (use a `.env` at repo root). On macOS/Linux: `source .venv/bin/activate` and launch from the project root.


### Legal
This project is for educational and personal use only. You are responsible for complying with LinkedIn’s Terms of Service and applicable laws.

## LinkedIn Job Agent

Small async Playwright script that logs into LinkedIn and lists fresh job postings matching your criteria. It searches using keywords and location, then prints matching roles to the terminal.

### Features
- **Headful browser automation**: Uses Playwright to log in and search jobs
- **Configurable search**: Edit keywords, location, and basic filters in `job_monitor/job_config.py`
- **.env-based secrets**: Keep your LinkedIn credentials out of source

### Prerequisites
- **Python**: 3.10+
- **Playwright browsers**: Installed via `python -m playwright install`
- macOS/Linux/Windows supported by Playwright (this repo was authored on macOS)

### Quick start
1) Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m playwright install chromium
```

2) Add credentials in a `.env` file inside `job_monitor/`

```ini
# job_monitor/.env
LINKEDIN_EMAIL=you@example.com
LINKEDIN_PASSWORD=your_password
```

3) Configure your search in `job_monitor/job_config.py`

```python
job_search_config = {
    "keywords": ["AI Intern", "Machine Learning Intern", "Data Science Intern"],
    "location": "India",
    "experience_level": ["Internship", "Entry level"],
    "remote": True,
    "posted_within_days": 1,
}
```

4) Run the monitor

```bash
cd job_monitor
python monitor.py
```

You should see a Chromium window open, the script will log in and then print any matching jobs to the terminal.

### How it works
- Loads credentials from `.env` with `python-dotenv`
- Launches Chromium in non-headless mode and signs in to LinkedIn
- Navigates to a jobs search URL built from your config and scrapes visible job cards
- Prints results like: `Title at Company — Location` and the job URL

### Adjusting behavior
- **Headless mode**: In `job_monitor/monitor.py`, change `headless=False` to `True` to run without a visible browser.
- **Filters**: The search URL currently applies a 24-hour posted filter and entry-level/internship filters. Tweak `job_monitor/monitor.py` or `job_config.py` if you need different behavior.

### Project layout
```text
.
├── job_monitor/
│   ├── __init__.py
│   ├── job_config.py       # Edit your keywords/location here
│   ├── monitor.py          # Main script
│   └── job_data.json       # Reserved for future persistence (currently unused)
├── requirements.txt
└── README.md
```

### Troubleshooting
- **Login loops or MFA prompts**: LinkedIn may challenge with 2FA or CAPTCHA. Because the browser is headful, you can complete challenges manually in the opened window. If it persists, try slower navigation or adjust selectors.
- **Selectors changed**: LinkedIn UI updates can break selectors used in `monitor.py`. Update selectors if elements are not found.
- **Playwright not installed correctly**: Ensure both the Python package and the browser binaries are installed: `pip install playwright` and `python -m playwright install chromium`.
- **Imports failing**: Run from inside the `job_monitor/` directory so `job_config.py` is importable as written.

### Security and usage notes
- Store credentials only in `.env` and never commit them.
- Automating LinkedIn may violate their Terms of Service and could lead to account restrictions. Use for personal, responsible automation and at your own risk.

### License
No license specified.


# linkedin_automation
# linkedin_automation
