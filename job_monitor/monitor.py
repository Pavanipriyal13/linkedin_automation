# job_monitor/monitor.py

import asyncio
import datetime
import json
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from job_config import job_search_config

load_dotenv()  # Load from .env

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

async def monitor_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Login if credentials are present; otherwise continue anonymously
        if LINKEDIN_EMAIL and LINKEDIN_PASSWORD:
            await page.goto("https://www.linkedin.com/login")
            await page.fill("input#username", LINKEDIN_EMAIL)
            await page.fill("input#password", LINKEDIN_PASSWORD)
            await page.click("button[type=submit]")
            try:
                await page.wait_for_url("https://www.linkedin.com/feed/", timeout=15000)
            except Exception:
                # Often redirects to checkpoint; allow manual intervention or continue to search
                print("⚠️ Did not reach feed. If a checkpoint or MFA is shown, please complete it in the opened browser.")
                await page.wait_for_timeout(5000)
        else:
            print("ℹ️ No credentials found. Proceeding without login.")

        # Search
        keyword = job_search_config["keywords"][0]
        location = job_search_config["location"]
        # Add Easy Apply filter (f_AL=true) where supported
        search_url = (
            f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
            f"&location={location}&f_TP=1&f_E=1%2C2&f_AL=true"
        )

        jobs = []
        try:
            await page.goto(search_url)
            await page.wait_for_selector(".job-card-container", timeout=20000)

            job_cards = await page.query_selector_all(".job-card-container")
        except Exception as e:
            print(f"⚠️ Could not locate job cards: {e}")
            job_cards = []

        for job_card in job_cards:
            try:
                # Try multiple selectors for robustness
                title_el = await job_card.query_selector("a.job-card-container__link, a.job-card-list__title, h3")
                company_el = await job_card.query_selector("a.job-card-container__company-name, span.job-card-container__primary-description, h4")
                location_el = await job_card.query_selector(".job-card-container__metadata-item, .job-card-container__metadata-item--location")
                link_el = await job_card.query_selector("a.job-card-container__link, a.job-card-list__title, a")

                title = (await title_el.inner_text()) if title_el else ""
                company = (await company_el.inner_text()) if company_el else ""
                location = (await location_el.inner_text()) if location_el else ""
                job_url = (await link_el.get_attribute("href")) if link_el else ""
                if job_url and job_url.startswith("/"):
                    job_url = f"https://www.linkedin.com{job_url}"

                # Do not pre-verify Easy Apply here; auto-apply will skip if not applicable

                if job_url:
                    jobs.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "url": job_url.strip(),
                        "timestamp": datetime.datetime.now().isoformat()
                    })

            except Exception as e:
                print(f"Error parsing job card: {e}")

        for job in jobs:
            print(f"\n🔹 {job['title']} at {job['company']} — {job['location']}\n{job['url']}\n")

        # Persist to job_data.json for the auto-apply step
        output = {
            "jobs": [
                {
                    "title": j["title"],
                    "company": j["company"],
                    "link": j["url"],
                    "timestamp": j["timestamp"],
                }
                for j in jobs
            ]
        }
        data_path = os.path.join(os.path.dirname(__file__), "job_data.json")
        with open(data_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"💾 Saved {len(jobs)} job(s) to {data_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(monitor_jobs())

