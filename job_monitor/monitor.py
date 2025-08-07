# job_monitor/monitor.py

import asyncio
import datetime
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

        # Login
        await page.goto("https://www.linkedin.com/login")
        await page.fill("input#username", LINKEDIN_EMAIL)
        await page.fill("input#password", LINKEDIN_PASSWORD)
        await page.click("button[type=submit]")
        await page.wait_for_url("https://www.linkedin.com/feed/")

        # Search
        keyword = job_search_config["keywords"][0]
        location = job_search_config["location"]
        search_url = (
            f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
            f"&location={location}&f_TP=1&f_E=1%2C2"
        )

        await page.goto(search_url)
        await page.wait_for_selector(".job-card-container")

        job_cards = await page.query_selector_all(".job-card-container")
        jobs = []

        for job_card in job_cards:
            try:
                title = await job_card.query_selector_eval("h3", "el => el.innerText")
                company = await job_card.query_selector_eval("h4", "el => el.innerText")
                location = await job_card.query_selector_eval(
                    ".job-card-container__metadata-item", "el => el.innerText"
                )
                job_url = await job_card.query_selector_eval("a", "el => el.href")

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

        await browser.close()

if __name__ == "__main__":
    asyncio.run(monitor_jobs())

