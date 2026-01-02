from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pages.basepage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage(BasePage):

        # ===== Locators =====
        BUY_MEDICINES_LINK = (By.LINK_TEXT, "Buy Medicines")
        SEARCH_BTN = (By.CLASS_NAME, "SearchPlaceholder_sRoot__ZK2aL")
        CART_ICON = (By.XPATH, "//a[@aria-label='Cart Icon']")
        SEARCH_INPUT = (By.ID, "searchProduct")


        # ===== Actions =====
        def open_home(self, url):
            self.open_url(url)

        # Link to the "Buy Medicines" section on the homepage
        def click_buy_medicines(self):
            self.click(self.BUY_MEDICINES_LINK)

        # Opens search bar for the search input
        def search(self, term: str, submit=True):
            self.click(self.SEARCH_BTN)

            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.SEARCH_INPUT))
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SEARCH_INPUT))

            self.type(self.SEARCH_INPUT, term, clear=True)
            if submit:
                self.press_key(self.SEARCH_INPUT, Keys.ENTER)
            self.wait_for_page_load()

        # Open cart page
        def open_cart(self):
            self.click(self.CART_ICON)
            self.wait_for_page_load()
