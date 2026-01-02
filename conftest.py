import allure
import pytest


from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager

from utils.config_reader import ConfigReader
from utils.logger import get_logger
from utils.screenshot_util import take_screenshot


logger = get_logger("conftest")


@pytest.fixture(scope="function")
def driver(request):
    browser = ConfigReader.get("browser").lower()
    base_url = ConfigReader.get("base_url")

    logger.info(f"Starting test: {request.node.name}")
    logger.info(f"Browser selected: {browser}")

    if browser == "edge":
        options = EdgeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")  # Suppress INFO and WARNING
        # edge_options.add_argument("--headless")
        driver = webdriver.Edge(
            # service=EdgeService(EdgeChromiumDriverManager().install()),
            service=EdgeService("resources/msedgedriver.exe"),
            options=options
        )

    elif browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")  # Suppress INFO and WARNING
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver.get(base_url)

    yield driver

    logger.info(f"Tearing down test: {request.node.name}")
    driver.quit()



# ========================================================================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver", None)
        if driver:
            screenshot_name = item.name
            screenshot_path = take_screenshot(driver, screenshot_name)

            logger.error(f"Test failed: {item.name}")
            logger.error(f"Screenshot saved at: {screenshot_path}")

            # Attach to Allure
            with open(screenshot_path, "rb") as image:
                allure.attach(
                    image.read(),
                    name=screenshot_name,
                    attachment_type=allure.attachment_type.PNG
                )

# ======================================================================================================

ALLURE_PATH = r"C:\VnV Training\ms edge driver\allure-2.36.0\allure-2.36.0\bin\allure.bat"  # adjust if needed


def pytest_unconfigure(config):
    import subprocess, os

    project_root = os.getcwd()
    results_dir = os.path.join(project_root, "reports")
    output_dir = os.path.join(project_root, "allure-reports")

    if not os.path.exists(results_dir):
        logger.info("No Allure results found. Skipping.")
        return

    logger.info("Generating Allure HTML...")

    cmd = [
        ALLURE_PATH,
        "generate",
        results_dir,
        "-o",
        output_dir,
        "--clean"
    ]

    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        logger.info(
            "Allure HTML report generated successfully at %s",
            os.path.join(output_dir, "index.html")
        )
    else:
        logger.error("Allure HTML generation failed.")



