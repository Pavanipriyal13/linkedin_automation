from auto_apply.config import CONFIG

async def fill_application_form(page):
    # Upload resume if needed
    upload_input = await page.query_selector("input[type='file']")
    if upload_input:
        await upload_input.set_input_files(CONFIG.RESUME_PATH)

    # Example: Fill custom fields (adjust based on actual fields)
    try:
        phone_input = await page.query_selector("input[aria-label='Phone number']")
        if phone_input:
            await phone_input.fill("9876543210")
    except:
        pass  # skip if field doesn't exist

    # Continue through steps
    next_button = await page.query_selector("button:has-text('Next')")
    if next_button:
        await next_button.click()
        await page.wait_for_timeout(1500)

    submit_button = await page.query_selector("button:has-text('Submit application')")
    if submit_button:
        await submit_button.click()
        return True
    return False
