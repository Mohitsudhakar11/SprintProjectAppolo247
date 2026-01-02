
from selenium.webdriver.common.by import By
from pages.basepage import BasePage

class ProductDetailPage(BasePage):
    # ===== Locators =====
    PRODUCT_TITLE = (By.XPATH, "//h1[contains(@class,'nj')]")
    ADD_TO_CART_BTN = (By.XPATH, "//div[contains(span,'Add to Cart')]")
    GO_TO_CART_BTN = (By.XPATH, "//span[text()='View Cart']")

    PRICE_LOC = (By.CSS_SELECTOR, "p.mH.fH.iT_")
    MRP_LOC = (By.XPATH, "//span[contains(@class,'gT_')]")
    DISCOUNT_LOC = (By.XPATH, "//span[contains(@class,'hT_')]")

    # ===== Actions =====
    # Get product title text
    def get_product_title(self) -> str:
        return self.get_text(self.PRODUCT_TITLE)

    # Get price, MRP, and discount details
    def get_pricing_info(self) -> dict:
        info = {
            "price": self.get_text(self.PRICE_LOC) if self.is_visible(self.PRICE_LOC) else None,
            "mrp": self.get_text(self.MRP_LOC) if self.is_visible(self.MRP_LOC) else None,
            "discount": self.get_text(self.DISCOUNT_LOC) if self.is_visible(self.DISCOUNT_LOC) else None
        }
        return info

    # Add product to cart and select quantity
    def add_to_cart(self,qty):
        # Some sites enable the button after variant selection—using JS click fallback may help
        if self.is_visible(self.ADD_TO_CART_BTN):
                self.click(self.ADD_TO_CART_BTN)
                quantity=(By.XPATH,
f"//div[contains(concat(' ', normalize-space(@class), ' '), ' aT ')]" \
        f"//ul[@class='lT']//p[starts-with(normalize-space(), '{qty}')]")
                self.click(quantity)
        self.wait_for_page_load()

    #open cart page after adding product
    def open_cart(self):
        # If an explicit "Go to Cart" appears after add, prefer that; else top cart icon
        if self.is_visible(self.GO_TO_CART_BTN):
            self.click(self.GO_TO_CART_BTN)
        else:
            cart_icon = (By.CSS_SELECTOR, " a[aria-label='Cart Icon'] ")
            self.click(cart_icon)
        self.wait_for_page_load()
