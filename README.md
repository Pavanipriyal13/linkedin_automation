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
