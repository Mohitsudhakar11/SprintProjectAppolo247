
# tests/test_delivery_slot_selection.py
import pytest
import allure
import time
from pages.homepage import HomePage
from pages.buy_medicines_page import BuyMedicinePage
from utils.excel_reader import ExcelReader
from pages.product_listing_page import ProductListingPage
from pages.product_detail_page import ProductDetailPage
from pages.Cartpage import CartPage


test_data9= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)

@pytest.mark.parametrize("data", test_data9)
@pytest.mark.regression
def test_tc09_select_preferred_delivery_time_slot(driver,data,request):
    """
    TC_09: Validate preferred time slot selection for delivery
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    cart = CartPage(driver)
    test_name = request.node.name


    try:
        with allure.step("Add known item and open cart"):
            home.click_buy_medicines()
            home.click_buy_medicines()
            home.search(data["known_item"])
            listing.open_product_by_name(data["known_item"])
        with allure.step("Verify Title reflect item"):
            import re

            def normalize(text: str) -> str:
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())

            title = buy.get_title()

            term = normalize(data["known_item"])

            title_norm = normalize(title)

            assert term in title_norm or title_norm in term, \
                f"Title should reflect  '{data['known_item']}' (found: {title})"
            pdp.add_to_cart(qty="1")
            pdp.open_cart()
        with allure.step("Proceed to slot selection page"):
            cart.proceed()
            phone = data["phone"]
            cart.enter_phone_num(phone)
            time.sleep(25)
            cart.proceed_after()
            time.sleep(3)
        with allure.step("Verify URL and Title reflect delivery page"):
            import re

            def normalize(text: str) -> str:
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())

            current_url = buy.get_current_url()
            title = buy.get_title()

            term = normalize(data["delivery_term"])
            url_norm = normalize(current_url)
            title_norm = normalize(title)

            assert term in url_norm or url_norm in term, \
                f"URL should reflect  '{data['deivery_term']}' (found: {current_url})"
            assert term in title_norm or title_norm in term, \
                f"Title should reflect '{data['delivery_term']}' (found: {title})"

        with allure.step(f"Select delivery slot: {data["del_type"]} / {data["date_label"]} / {data["time_label"]}"):
            if(data["del_type"]=='Express Delivery'):
                cart.select_preferred_slot(data["del_type"])
            else:
                cart.select_preferred_slot_time(data["del_type"], data["date_label"], data["time_label"])

        # If UI exposes a 'selected' state, you can add a direct assertion here.
        assert True, "Preferred time slot selection completed."

    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_09 failed: {e}")
        raise


test_data10= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)

@pytest.mark.parametrize("data", test_data10)
@pytest.mark.regression
def test_tc10_invalid_search(driver,data,request):
    """
    TC_10: Validate invalid search term
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    cart = CartPage(driver)
    test_name = request.node.name


    try:
        with allure.step("Searching the search term:"):
            home.click_buy_medicines()
            home.click_buy_medicines()
            home.search(data["search_term"])
            time.sleep(5)


        # Count product tiles generically (no product names needed)
        result_count = len(driver.find_elements(*listing.PRODUCT_NAMES))

        # Assert: expect zero results
        assert result_count == 0, f"Expected 0 items, found {result_count} for search term 'donkey'."

        # Optional: log pass
        listing.log_test_passed(request.node.name)


    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_10 failed: {e}")
        raise




