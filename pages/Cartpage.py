
import re
import time

from selenium.webdriver.common.by import By
from pages.basepage import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

class CartPage(BasePage):
    # ===== Locators =====
    SUBTOTAL_LABEL = (By.XPATH, "//p[contains(@class,'CartSummary_priceCol__pCedm')]  /span[contains(text(),'To Pay')]")
    SUBTOTAL_VALUE = (By.XPATH, "//p[contains(@class,'CartSummary_priceCol__pCedm CartSummary_priceColright__OJh59')]  /span")

    PROCEED_BTN = (By.XPATH, "//button[contains(., 'Proceed') or contains(., 'Checkout')]")
    PROCEED_BTN_LATER=(By.XPATH, "//button[contains(., 'PROCEED') or contains(., 'Checkout')]")
    PROCEED_BTN_FINAL=(By.XPATH,"//button[contains(.,'PROCEED')]")
    # EMPTY_MSG = (By.XPATH, "//div[contains(@class,'EmptyCart_noCartItems__')]/p[contains(normalize-space(.),'YOUR CART IS EMPTY')]")
    QTY_BTN = (By.CLASS_NAME, "MedicineProductCard_optionHead__IDGH+")

    # Delivery slot page (after proceed)
    SLOT_BY_TEXT_FMT = "//label[contains(., '{TEXT}') or .//span[contains(., '{TEXT}')]]"

    # ===== Helpers =====
    # Convert currency string to int
    def _amount_to_int(self, text: str) -> int | None:
        digits = re.sub(r"[^0-9]", "", text or "")
        return int(digits) if digits else None

    # ===== Actions =====
    # Change quantity for a specific product
    def change_quantity(self, prod_name,qty):
       qty_btn=(By.XPATH,f"""//h2[contains(normalize-space(.), '{prod_name}')]   
       /ancestor::div[contains(@class,'MedicineProductCard_productDetailsRoot__') or contains(@class,'MedicineProductCard_cardRoot__')][1]  
        //div[contains(@class,'MedicineProductCard_rightBx__')]  
         //div[contains(@class,'MedicineProductCard_optionHead__')]   
         /p[starts-with(normalize-space(.), 'Qty')]
""")
       self.click(qty_btn)
       option=(By.XPATH,f"""
 //div[contains(@class,'MedicineProductCard_list__')] 
 //p[contains(@class,'MedicineProductCard_ddQty__')][normalize-space(text()[1])='{qty}']
""")
       self.click(option)

    # Get subtotal text
    def get_subtotal_text(self) -> str | None:
        if self.is_visible(self.SUBTOTAL_VALUE):
            return self.get_text(self.SUBTOTAL_VALUE)
        return None

    # Get subtotal amount as int
    def get_subtotal_amount(self) -> int | None:
        txt = self.get_subtotal_text()
        return self._amount_to_int(txt) if txt else None



    def remove_all_items(self):
        wait = WebDriverWait(self.driver, self.timeout)

        # Wait for cart to be present (title/checkout OR list)
        cart_ready = (By.XPATH,
                      "//h1[contains(.,'Cart')]"
                      " | //button[contains(.,'Checkout') or contains(.,'Proceed')]"
                      " | //div[contains(@class,'cart')]"
                      )
        try:
            wait.until(EC.presence_of_element_located(cart_ready))
        except TimeoutException:
            self.logger.warning("Cart anchor not present; proceeding best effort")

        # Broader, more stable remove locator
        REMOVE_LOC = (By.XPATH,
                      "//button[contains(.,'Remove')]"
                      " | //*[(self::button or @role='button') and contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'remove')]"
                      " | //div[contains(@class,'delete') or contains(@class,'remove')]"
                      )

        # Attempt removal loop
        while True:
            buttons = [b for b in self.driver.find_elements(*REMOVE_LOC) if b.is_displayed()]
            self.logger.debug(f"[Cart] visible remove buttons = {len(buttons)}")

            if not buttons:
                # small grace period for lazy render; refetch once
                time.sleep(0.5)
                buttons = [b for b in self.driver.find_elements(*REMOVE_LOC) if b.is_displayed()]
                if not buttons:
                    break  # nothing to remove

            btn = buttons[0]
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)

            try:
                wait.until(EC.element_to_be_clickable(btn))
                btn.click()
                self.logger.debug("[Cart] Remove clicked (native)")
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
                self.logger.debug("[Cart] Remove clicked (JS fallback)")

            # Wait for item to be removed (staleness or count drop)
            try:
                wait.until(EC.staleness_of(btn))
            except TimeoutException:
                prev = len(buttons)
                wait.until(lambda d: len([x for x in d.find_elements(*REMOVE_LOC) if x.is_displayed()]) < prev)

            self.wait_for_page_load()

        self.wait_for_page_load()

    def is_empty(self, timeout=5) -> bool:
        """
        Cart is considered empty when Proceed/Checkout button is NOT visible.

        """
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.visibility_of_element_located(self.PROCEED_BTN)
            )
            return True
        except TimeoutException:
            # Proceed still visible after timeout → not empty
            return False

    # Click Proceed/Checkout
    def proceed(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.PROCEED_BTN))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PROCEED_BTN))
        if self.is_visible(self.PROCEED_BTN) and self.is_enabled(self.PROCEED_BTN):
            self.click(self.PROCEED_BTN)
            self.wait_for_page_load()

    # Click Proceed (variant)
    def proceed_after(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.PROCEED_BTN_LATER))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PROCEED_BTN_LATER))
        if self.is_visible(self.PROCEED_BTN_LATER) and self.is_enabled(self.PROCEED_BTN_LATER):
            self.click(self.PROCEED_BTN_LATER)
            self.wait_for_page_load()

    # Check if checkout is available
    def is_checkout_available(self) -> bool:
        return self.is_visible(self.PROCEED_BTN) and self.is_enabled(self.PROCEED_BTN)

    # Select delivery type
    def select_preferred_slot(self, del_type: str):
        delivery_type = (By.XPATH, f"//div[contains(@class,'header__EA7WQ')] /p[contains(text(),'{del_type}')]")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(delivery_type))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(delivery_type))
        self.scroll_into_view(delivery_type)
        self.js_click(delivery_type)  # often radio/label combos need JS click

    # Select delivery date and time
    def select_preferred_slot_time(self, del_type: str,date:str,time:str):
        delivery_type = (By.XPATH, f"//div[contains(@class,'header__EA7WQ')] /p[contains(text(),'{del_type}')]")
        self.scroll_into_view(delivery_type)
        self.js_click(delivery_type)
        slot=(By.XPATH,"//div[@class='preferSlotDD__AYRBh'] //div[@class='dayTimeComponent__Cxe17']")
        self.js_click(slot)
        slot_opt=(By.XPATH,f" //span[normalize-space(.)='{date}']   /ancestor::div[contains(@class,'root__')][1]   /following-sibling::div[contains(@class,'list__')]   /div[contains(@class,'label__')][normalize-space(.)='{time}']")
        self.js_click(slot_opt)

    # Final checkout and select Pay on Delivery
    def final_checkout(self,pay_type:str):
        PAY_BTN = (By.XPATH, f"//button[contains(., '{pay_type}') ]")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.PROCEED_BTN_FINAL))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PROCEED_BTN_FINAL))
        if self.is_visible(self.PROCEED_BTN_FINAL) and self.is_enabled(self.PROCEED_BTN_FINAL):
            self.click(self.PROCEED_BTN_FINAL)
            self.wait_for_page_load()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(PAY_BTN))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(PAY_BTN))

        self.click(PAY_BTN)
        self.wait_for_page_load()

    ENTER_NUM = (By.CSS_SELECTOR, "input[name='mobileNumber']")

    def enter_phone_num(self, phone_num):
        element = self.wait.until(EC.visibility_of_element_located(self.ENTER_NUM))
        element.send_keys(phone_num)
        self.press_key(self.ENTER_NUM, Keys.ENTER)

    # Log test status
    def log_test_passed(self, test_name):
        self.logger.info(f"Test passed for : {test_name}")




