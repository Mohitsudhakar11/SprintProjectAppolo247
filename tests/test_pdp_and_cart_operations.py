import time

# tests/test_pdp_and_cart_operations.py
import pytest
import allure
import itertools

from pages.homepage import HomePage
from utils.excel_reader import ExcelReader
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.buy_medicines_page import BuyMedicinePage
from pages.product_listing_page import ProductListingPage
from pages.product_detail_page import ProductDetailPage
from pages.Cartpage import CartPage



test_data5= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
@pytest.mark.regression
@pytest.mark.parametrize("data", test_data5)
def test_tc05_validate_pdp_for_known_item(driver,data,request):
    """
    TC_05: Validate PDP - title, MRP, selling price, discount tag for a known item
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    test_name = request.node.name

    try:
        with allure.step("Navigate to known item PDP"):
            home.click_buy_medicines()
            home.search(data["known_item"])
            listing.open_product_by_name(data["known_item"])


        with allure.step("Verify PDP fields"):
            title = pdp.get_product_title()
            info = pdp.get_pricing_info()
            pdp.logger.info(f"PDP Title: {title}")
            pdp.logger.info(f"PDP Pricing: {info}")

            assert data["known_item"].lower() in (title or "").lower(), "PDP title should match known item"
            assert info.get("price"), "Selling price should be visible on PDP"
            assert info.get("mrp"), "MRP should be visible on PDP"
            # Discount label may be optional; assert visibility when present in UI
            assert info.get("discount") is not None, "Discount label should be visible (when applicable)"

    except Exception as e:
        pdp.capture_screenshot(test_name)
        pdp.logger.error(f"TC_05 failed: {e}")
        raise



test_data6_1= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
test_data6_2= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_2"
)
cases = list(itertools.product(test_data6_1, test_data6_2))
@pytest.mark.regression
@pytest.mark.parametrize(("data","dataa"),cases)
def test_tc06_add_to_cart_and_verify_subtotal_for_qty_2(driver,data,dataa,request):
    
    """TC_06: Add item to cart → open cart → set quantity=2 → verify subtotal updates
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    cart = CartPage(driver)
    test_name = request.node.name

    try:
        with allure.step("Add known item to cart"):
            home.click_buy_medicines()
            home.click_buy_medicines()
            home.search(data["known_item"])
            listing.open_product_by_name(data["known_item"])

            pdp.add_to_cart(dataa["qty"])
            with allure.step("Verify Title reflect item"):
                import re

                def normalize(text: str) -> str:
                    return re.sub(r'[^a-z0-9]', '', (text or '').lower())

                title = buy.get_title()

                term = normalize(data["known_item"])

                title_norm = normalize(title)

                assert term in title_norm or title_norm in term, \
                    f"Title should reflect '{data['known_item']}' (found: {title})"

        with allure.step("Open Cart and validate subtotal"):
            pdp.open_cart()
            first_subtotal = cart.get_subtotal_amount()
            cart.logger.info(f"Cart subtotal initially(int digits): {first_subtotal}")


        with allure.step("Change cart quantity to 2 and validate subtotal"):
            cart.change_quantity(data["known_item"],dataa["final_qty"])
            second_subtotal = cart.get_subtotal_amount()
            cart.logger.info(f"Cart subtotal after increaing quantity(int digits): {second_subtotal}")

            assert first_subtotal < second_subtotal , \
                "Subtotal should be positive after quantity change"


    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_06 failed: {e}")
        raise



test_data7_1= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
test_data7_2= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_2"
)
cases = list(itertools.product(test_data7_1, test_data7_2))
@pytest.mark.regression
@pytest.mark.parametrize(("data","dataa"),cases)
def test_tc07_remove_item_and_validate_empty_cart(driver,data,dataa,request):
    """
    TC_07: Remove item(s) from cart and validate 'YOUR CART IS EMPTY' state
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    cart = CartPage(driver)
    pdp = ProductDetailPage(driver)
    test_name = request.node.name

    try:
        with allure.step("Precondition: add one item to cart"):
            home.click_buy_medicines()
            home.search(data["known_item"])
            listing.open_product_by_name(data["known_item"])

            pdp.add_to_cart(dataa["qty"])
            pdp.open_cart()


        with allure.step("Remove all items and verify empty cart"):

            cart.remove_all_items()
            assert cart.is_empty(), "Empty cart message should be displayed after removal"

    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_07 failed: {e}")
        raise


test_data8= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
@pytest.mark.regression
@pytest.mark.parametrize("data",test_data8)
def test_tc08_checkout_unavailable_when_cart_empty(driver,data,request):

    """TC_08: Validate that checkout/proceed is unavailable when cart is empty
    """
    home = HomePage(driver)
    cart = CartPage(driver)
    test_name = request.node.name
    buy = BuyMedicinePage(driver)

    try:
        with allure.step("Open Cart from header"):
            home.click_buy_medicines()
            home.open_cart()
        with allure.step("Verify URL and Title reflect product type"):
            import re

            def normalize(text: str) -> str:
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())

            current_url = buy.get_current_url()
            title = buy.get_title()

            term = normalize(data["cart_term"])
            url_norm = normalize(current_url)
            title_norm = normalize(title)

            assert term in url_norm or url_norm in term, \
                f"URL should reflect  '{data['cart_term']}' (found: {current_url})"
            assert term in title_norm or title_norm in term, \
                f"Title should reflect  '{data['cart_term']}' (found: {title})"
        with allure.step("Ensure empty and verify checkout disabled"):
            if not cart.is_empty():
                cart.remove_all_items()
            assert not cart.is_checkout_available(), "Checkout/Proceed should be unavailable for empty cart"

    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_08 failed: {e}")
        raise
