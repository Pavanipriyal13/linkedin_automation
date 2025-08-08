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
    try:
        await page.wait_for_url("**/feed/**", timeout=15000)
    except Exception:
        # If checkpoint, allow time for manual intervention
        await page.wait_for_timeout(5000)
    # Persist session storage for reuse
    try:
        await page.context.storage_state(path="auth.json")
    except Exception:
        pass

async def auto_apply_to_job(page, job_link):
    try:
        if job_link.startswith("/"):
            job_link = f"https://www.linkedin.com{job_link}"
        await page.goto(job_link)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1000)

        # Extract job title and company name (non-blocking)
        title_el = await page.query_selector("h1")
        company_el = await page.query_selector("a.topcard__org-name-link, span.topcard__flavor")
        job_title = (await title_el.inner_text()) if title_el else "Unknown Title"
        company_name = (await company_el.inner_text()) if company_el else "Unknown Company"
        print(f"👀 Viewed job: {job_title.strip()} at {company_name.strip()}")

        with open("viewed_jobs.log", "a") as log:
            log.write(f"{job_title.strip()} at {company_name.strip()} — {job_link}\n")

        # Try clicking an apply button (various variants)
        apply_selectors = [
            "button:has-text('Easy Apply')",
            "button[aria-label*='Easy Apply']",
            "[data-control-name='jobdetails_topcard_inapply']",
            "button:has-text('Quick Apply')",
            "button:has-text('Apply now')",
            "button:has-text('Apply')",
        ]
        applied_clicked = False
        for selector in apply_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    applied_clicked = True
                    break
            except Exception:
                continue

        if not applied_clicked:
            print(f"ℹ️ No applicable apply button found; skipping: {job_link}")
            return "skipped"

        # Attach resume early if the input appears
        await upload_resume(page)
        success = await fill_application_form(page)
        if success:
            print(f"✅ Applied to: {job_link}")
            # Log successful application
            try:
                from datetime import datetime
                with open("applied_jobs.log", "a") as applied_log:
                    applied_log.write(
                        f"{datetime.now().isoformat()} | {job_title.strip()} | {company_name.strip()} | {job_link}\n"
                    )
            except Exception:
                pass
        else:
            print(f"⚠️ Could not complete application for: {job_link}")
        return "ok"
    except Exception as e:
        message = str(e)
        print(f"❌ Error applying to {job_link}: {message}")
        if "Target page, context or browser has been closed" in message or "net::ERR_ABORTED" in message:
            return "restart"
        return "error"

async def apply_to_jobs():
    playwright, browser, page = await launch_browser(headless=False)
    await login_to_linkedin(page)

    with open("job_monitor/job_data.json") as f:
        job_data = json.load(f)

    for job in job_data.get("jobs", []):
        job_link = job["link"] if isinstance(job, dict) else job
        result = await auto_apply_to_job(page, job_link)
        if result == "restart":
            # Attempt restart and retry once
            try:
                await browser.close()
            except Exception:
                pass
            playwright, browser, page = await launch_browser(headless=False)
            await login_to_linkedin(page)
            _ = await auto_apply_to_job(page, job_link)

    try:
        await browser.close()
    finally:
        await playwright.stop()
