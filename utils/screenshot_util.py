
import os
from datetime import datetime

SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "screenshots",
)
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def take_screenshot(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{name}_{timestamp}.png"
    file_path = os.path.join(SCREENSHOT_DIR, file_name)

    try:
        driver.save_screenshot(file_path)
    except Exception as e:
        print(f"Screenshot capture failed: {e}")
    return file_path


