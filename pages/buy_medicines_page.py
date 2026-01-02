from selenium.webdriver.common.by import By
from pages.basepage import BasePage
import time

class BuyMedicinePage(BasePage):
    # ===== Locators =====
    NUTRITIONAL_DRINKS_SUPPLEMENTS = (
        By.XPATH, "// a[text() = 'Nutritional Drinks & Supplements']"
    )

    # ===== Actions =====
    def open_nutritional_drinks_and_supplements(self):
        # Scroll to the element and click
        self.scroll_into_view(self.NUTRITIONAL_DRINKS_SUPPLEMENTS)
        self.click(self.NUTRITIONAL_DRINKS_SUPPLEMENTS)
        self.wait_for_page_load()
        self.actions.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, "body"), 1, 1).perform()
        time.sleep(5)
