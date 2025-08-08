from auto_apply.config import CONFIG

async def upload_resume(page):
    try:
        resume_input = await page.query_selector("input[type='file']")
        await resume_input.set_input_files(CONFIG.RESUME_PATH)
        print("📎 Resume attached.")
        return True
    except Exception as e:
        print(f"❌ Resume upload failed: {e}")
        return False
