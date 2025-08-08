import asyncio
import json
import os

from auto_apply.apply import apply_to_jobs


def load_job_links(path="job_monitor/job_data.json"):
    if not os.path.exists(path):
        print(f"❌ job_data.json not found at {path}")
        return []
    with open(path, "r") as f:
        try:
            data = json.load(f)
            return data.get("jobs", [])
        except json.JSONDecodeError:
            print("❌ Failed to parse job_data.json")
            return []


async def main():
    job_links = load_job_links()

    if not job_links:
        print("📭 No jobs found in job_monitor/job_data.json. Run job_monitor/monitor.py first.")
        return

    print(f"✅ Found {len(job_links)} job(s) to apply.\n")

    await apply_to_jobs()
    print("✅ All jobs processed.")


if __name__ == "__main__":
    asyncio.run(main())

