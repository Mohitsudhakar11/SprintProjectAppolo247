import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from decimal import Decimal, InvalidOperation
from typing import Optional

from pages.basepage import BasePage
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

class ProductListingPage(BasePage):
    # ===== Generic Locators =====
    # Sort dropdown button
    SORT_BUTTON = (By.XPATH, "//div[starts-with(@class,'ProductSortWeb_ddMain__')]//button[contains(@class,'ProductSortWeb_sortRoot__')]")

    # Price text in product card
    PRICE_IN_CARD = (By.XPATH,
                     "//div[contains(@class,'QR_')]   //p[contains(@class,'SR_') and not(.//span[contains(@class,'TR_')])]")

    # Product card by name
    PRODUCT_CARD = lambda self, name: (
        By.XPATH,
        f"//div[contains(@class,'A_')]"
        f"[.//div[@class='J_']/h2[contains(text(),'{name}')]]"
    )
    # Visible product names
    PRODUCT_NAMES = (By.XPATH,"//div[@class='J_']/h2[contains(@class, 'O_')]")

    # Add to Cart button (inside a product card)
    ADD_TO_CART = (
        By.XPATH,
        ".//button[contains(span,'Add')]"
    )
    # ===== Category navigation =====


    def open_category(self, category_label: str):
            # Target tile for category
            whey_link = (By.XPATH, f"//a[contains(.,'{category_label}')]")

            self.scroll_into_view(whey_link)
            time.sleep(1)

            # Offset scroll to avoid sticky header overlap (move 150px down

            try:
                # Try normal click first
                self.click(whey_link)
            except Exception as e:
                # If intercepted, wait briefly and use JS click fallback
                self.logger.warning(f"Click intercepted on category '{category_label}', using JS click. Details: {e}")
                self.js_click(whey_link)

            self.wait_for_page_load()

    # ===== Sorting =====
    def select_sort_option(self, sort: str):
        # e.g., "Price: Low to High", "Price: High to Low", "Popularity", "No. of tests High to Low"

        try:
            self.click(self.SORT_BUTTON)
        except Exception:
            self.js_click(self.SORT_BUTTON)
        time.sleep(5)
        option = (
            By.XPATH,
            f"//label[normalize-space()='{sort}']"
        )
        self.wait.until(EC.visibility_of_element_located(option))


        try:
            self.click(option)
        except Exception:
            self.js_click(option)


        self.wait_for_page_load()

    # ===== Filters =====
    # Filter by product type
    def filter_by_product_type(self, product_type: str):
        # Left filter: "Shop by Product Type" → label or checkbox
        opt = (By.XPATH, f"//div[@class='F'] //a[@aria-label='{product_type}']")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(opt))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(opt))
        if self.is_visible(opt) and self.is_enabled(opt):
            self.click(opt)
            self.wait_for_page_load()
        #self.scroll_into_view(opt)
        # self.js_click(opt) # sometimes filters are overlayed
        time.sleep(3)
        self.wait_for_page_load()

    # Open brand filter and select a brand
    def filter_by_type(self, filter: str, brand_name: str, timeout: int = 25):
        wait = WebDriverWait(self.driver, timeout)

        # # 1) Common loader in your logs
        # loader = (By.CSS_SELECTOR, ".NavigationLoader_navigationLoader__OAPCS")
        #
        # def wait_loader_gone():
        #     try:
        #         wait.until(EC.invisibility_of_element_located(loader))
        #     except TimeoutException:
        #         # If it never appears, proceed
        #         pass
        #
        # # Initial guard
        # self.wait_for_page_load()
        # wait_loader_gone()

        # 2) Click the filter header (minimal change: keep your locator)
        filter_opt = (By.XPATH, f"//span[contains(.,'{filter}')]")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(filter_opt))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(filter_opt))

        self.js_click(filter_opt)
        time.sleep(3)


        # 3) Select the brand checkbox (keep your locator, add better waits)
        brand_opt = (By.XPATH,f"//label[contains(., '{brand_name}')]")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(brand_opt))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(brand_opt))

        self.js_click(brand_opt)
        time.sleep(3)
        self.wait_for_page_load()




    # ===== Products =====
    # Open product by index from the list
    def select_product(self, product_number: str):
        element=int(product_number)
        locator=(By.XPATH,f"(//div[contains(@class,'A_')])[{element}]")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
        self.click(locator)
        self.wait_for_page_load()

    # Return visible product names
    def get_visible_product_names(self):

        locator = (By.XPATH, "//div[@class='J_']/h2[contains(@class, 'O_')]")
        elems = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(locator)
        )
        return [e.text.strip() for e in elems if e.text.strip()]

    # Open product by exact name
    def open_product_by_name(self, prodname: str):

        locator = (By.XPATH,f"//img[@title='{prodname}']")
        self.scroll_to_center(locator)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
        self.js_click(locator)

        #self.scroll_into_view(target)
       # self.click(target)
        self.wait_for_page_load()

    # ===== Price utilities (useful for Sort validations) =====
    # Convert price text to int
    def _extract_amount(self, text: str) -> int | None:
        # Handles ₹1,999.00 → 1999
        # digits = re.sub(r"[^0-9]", "", text or "")
        # return int(digits) if digits else None

        if not text:
            return None
        s = text.replace("₹", "").replace("Rs.", "").replace("Rs", "")
        s = s.replace(",", "").strip()
        m = re.search(r"(\d+(?:\.\d+)?)", s)
        if not m:
            return None
        try:
            return (m.group(0))
        except InvalidOperation:
            return None

    # Get list of visible prices from card
    def get_card_prices(self) -> list[int]:
        # Collect visible price amounts from listing
        price_nodes = self.get_elements(self.PRICE_IN_CARD)
        values = []
        for p in price_nodes:
            val = self._extract_amount(p.text)
            if val is not None:
                values.append(val)
        return values

    # Check prices sorted ascending
    def is_sorted_low_to_high(self) -> bool:
        vals = self.get_card_prices()
        return vals == sorted(vals) and len(vals) > 1

    # Check prices sorted descending
    def is_sorted_high_to_low(self) -> bool:
        vals = self.get_card_prices()
        return vals == sorted(vals, reverse=True) and len(vals) > 1

    # ===== Add Product To Cart =====
    # Add product by name and return its price
    def add_product_to_cart_and_get_price(self, prodname):
        self.scroll_into_view(self.PRODUCT_CARD(prodname))
        time.sleep(3)
        card = self.get_element(self.PRODUCT_CARD(prodname))

        price_text = card.find_element(*self.PRODUCT_PRICE).text
        price = float(price_text.replace("₹", "").replace(",", "").strip())
        self.logger.info(f"Collected {prodname} Price: {price}")

        card.find_element(*self.ADD_TO_CART).click()
        self.logger.info(f"Added {prodname} to cart.")

        return price

    # Scroll element to center of viewport
    def scroll_to_center(self, locator, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'nearest'});", el
        )

    # Log test pass info
    def log_test_passed(self, test_name):
        self.logger.info(f"Test passed for : {test_name}")
