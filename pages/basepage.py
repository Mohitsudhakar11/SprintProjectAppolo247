from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from utils.config_reader import ConfigReader
from utils.logger import get_logger
from utils.screenshot_util import take_screenshot


class BasePage:

    def __init__(self, driver, timeout=ConfigReader.get("timeout")):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.actions = ActionChains(driver)
        self.logger = get_logger(self.__class__.__name__)
        self.timeout = timeout

    # ===============================
    # Element Finders
    # ===============================

    def get_element(self, locator):
        self.logger.debug(f"Finding element: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator))

    def get_elements(self, locator):
        self.logger.debug(f"Finding elements: {locator}")
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    # ===============================
    # Basic Actions
    # ===============================

    def click(self, locator):
        self.logger.info(f"Clicking on element: {locator}")
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text, clear=True):
        self.logger.info(f"Typing into element: {locator} | Text: {text}")
        element = self.get_element(locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def press_key(self, locator, key):
        self.logger.info(f"Pressing key {key} on element: {locator}")
        self.get_element(locator).send_keys(key)

    def get_text(self, locator):
        text = self.get_element(locator).text
        self.logger.debug(f"Text from {locator}: {text}")
        return text

    def is_visible(self, locator):
        try:
            return self.get_element(locator).is_displayed()
        except TimeoutException:
            return False

    def is_enabled(self, locator):
        return self.get_element(locator).is_enabled()

    # ===============================
    # Wait Utilities
    # ===============================

    def wait_for_presence(self, locator):
        self.logger.debug(f"Waiting for presence: {locator}")
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_invisibility(self, locator):
        self.logger.debug(f"Waiting for invisibility: {locator}")
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_url_contains(self, text):
        self.logger.debug(f"Waiting for URL to contain: {text}")
        return self.wait.until(EC.url_contains(text))

    def wait_for_page_load(self):
        self.logger.debug("Waiting for page load completion")
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # ===============================
    # JavaScript Helpers
    # ===============================

    def js_click(self, locator):
        self.logger.info(f"JS clicking on element: {locator}")
        element = self.get_element(locator)
        self.driver.execute_script("arguments[0].click();", element)

    def scroll_into_view(self, locator):
        self.logger.debug(f"Scrolling into view: {locator}")
        element = self.get_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # ===============================
    # Mouse Actions
    # ===============================

    def hover(self, locator):
        self.logger.info(f"Hovering over element: {locator}")
        element = self.get_element(locator)
        self.actions.move_to_element(element).perform()

    # ===============================
    # Browser Navigation
    # ===============================

    def open_url(self, url):
        self.logger.info(f"Opening URL: {url}")
        self.driver.get(url)
        self.wait_for_page_load()

    def refresh_page(self):
        self.logger.info("Refreshing page")
        self.driver.refresh()
        self.wait_for_page_load()

    def get_current_url(self):
        return self.driver.current_url

    def get_title(self):
        return self.driver.title

    # ===============================
    # Window / Tab Handling
    # ===============================

    def switch_to_new_window(self):
        self.logger.info("Switching to new window")
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def switch_to_parent_window(self):
        self.logger.info("Switching to parent window")
        self.driver.switch_to.window(self.driver.window_handles[0])

    # ===============================
    # Screenshots
    # ===============================

    def capture_screenshot(self, name):
        self.logger.info(f"Capturing screenshot: {name}")
        take_screenshot(self.driver, name)







