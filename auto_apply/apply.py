import asyncio
import json
from auto_apply.config import CONFIG
from auto_apply.browser import launch_browser
from auto_apply.autofill import fill_application_form
from auto_apply.resume_uploader import upload_resume

async def login_to_linkedin(page):
    await page.goto("https://www.linkedin.com/login")
    await page.fill("input#username", CONFIG.USERNAME or "")
    await page.fill("input#password", CONFIG.PASSWORD or "")

    await page.click("button[type='submit']")
    await page.wait_for_timeout(3000)

async def auto_apply_to_job(page, job_link):
    try:
        await page.goto(job_link)
        await page.wait_for_timeout(3000)

        # Extract job title and company name
        job_title = await page.text_content("h1") or "Unknown Title"
        company_name = await page.text_content("a.topcard__org-name-link, span.topcard__flavor") or "Unknown Company"
        print(f"👀 Viewed job: {job_title.strip()} at {company_name.strip()}")

        with open("viewed_jobs.log", "a") as log:
            log.write(f"{job_title.strip()} at {company_name.strip()} — {job_link}\n")

        # Try clicking Easy Apply
        easy_apply_btn = await page.wait_for_selector("button:has-text('Easy Apply')", timeout=5000)
        await easy_apply_btn.click()
        await page.wait_for_timeout(2000)

        # Attach resume early if the input appears
        await upload_resume(page)
        success = await fill_application_form(page)
        if success:
            print(f"✅ Applied to: {job_link}")
        else:
            print(f"⚠️ Could not complete application for: {job_link}")
    except Exception as e:
        print(f"❌ Error applying to {job_link}: {e}")

async def apply_to_jobs():
    playwright, browser, page = await launch_browser(headless=False)
    await login_to_linkedin(page)

    with open("job_monitor/job_data.json") as f:
        job_data = json.load(f)

    for job in job_data.get("jobs", []):
        job_link = job["link"] if isinstance(job, dict) else job
        await auto_apply_to_job(page, job_link)

    await browser.close()
    await playwright.stop()
