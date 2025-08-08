from auto_apply.config import CONFIG


async def upload_resume(page):
    try:
        selectors = [
            "input[type='file']",
            "input[type='file'][accept*='pdf']",
            "input[type='file'][name*='file']",
        ]
        resume_input = None
        # Try a few times to allow modal content to render
        for _ in range(5):
            for sel in selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        resume_input = el
                        break
                except Exception:
                    continue
            if resume_input:
                break
            await page.wait_for_timeout(1000)

        if not resume_input:
            print("ℹ️ Resume file input not found yet.")
            return False

        await resume_input.set_input_files(CONFIG.RESUME_PATH)
        print("📎 Resume attached.")
        return True
    except Exception as e:
        print(f"❌ Resume upload failed: {e}")
        return False
