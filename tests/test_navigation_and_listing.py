
# tests/test_navigation_and_listing.py
import pytest
import allure
import time
from pages.homepage import HomePage
from utils.excel_reader import ExcelReader
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.buy_medicines_page import BuyMedicinePage
from pages.product_listing_page import ProductListingPage



@pytest.mark.smoke
def test_tc01_navigate_to_nutritional_drinks_and_supplements(driver, request,data):
    """
    TC_01: Validate navigation to Nutritional Drinks & Supplements page via Buy Medicines
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    test_name = request.node.name

    try:
        with allure.step("Click 'Buy Medicines' from Home"):
            home.click_buy_medicines()

        with allure.step("Open 'Nutritional Drinks & Supplements'"):
            buy.open_nutritional_drinks_and_supplements()

        with allure.step("Verify URL & Title reflect category"):
            current_url = buy.get_current_url()
            title = buy.get_title()
            buy.logger.info(f"URL after navigation: {current_url}")
            buy.logger.info(f"Title after navigation: {title}")

            assert any(k in current_url.lower() for k in ["nutritional", "supplement"]), \
                "URL should reflect Nutritional Drinks & Supplements"
            assert any(k in title.lower() for k in ["nutritional", "supplement", "buy medicines"]), \
                "Title should reflect Nutritional Drinks & Supplements"

    except Exception as e:
        buy.capture_screenshot(test_name)
        buy.logger.error(f"TC_01 failed: {e}")
        raise

test_data2 = ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)

@pytest.mark.regression
@pytest.mark.parametrize("data", test_data2)
def test_tc02_sort_low_to_high_in_whey_proteins(driver,data,request):
    """
    TC_02: Validate sorting from Price: Low to High under Proteins
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    test_name = request.node.name

    try:
        with allure.step("Navigate: Buy Medicines → Nutritional Drinks & Supplements"):
            home.click_buy_medicines()
            buy.open_nutritional_drinks_and_supplements()

        with allure.step("Apply filter: Product Type → Protein"):
            listing.filter_by_product_type(data["product_type"])

        with allure.step("Apply sort: Price: Low to High"):
            listing.select_sort_option(data["sort_type"])

        with allure.step("Verify results are not empty"):
            names = listing.get_visible_product_names()
            listing.logger.info(f"Names after 'Protein' filter: {names}")
            assert len(names) > 0, "Product list should not be empty"


        with allure.step("Verify prices after sort"):
            names = listing.get_card_prices()
            listing.logger.info(f"prices after 'sort' filter: {names}")

        with allure.step("Assert ascending price order"):
            assert listing.is_sorted_low_to_high(), "Products should be sorted Low → High"

    except Exception as e:
        listing.capture_screenshot(test_name)
        listing.logger.error(f"TC_02 failed: {e}")
        raise


test_data3 = ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)

@pytest.mark.regression
@pytest.mark.parametrize("data", test_data3)
def test_tc03_filter_by_product_type_protein(driver,data, request):
    """
    TC_03: Validate filtering by Product Type = Protein
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    test_name = request.node.name
    current_url = buy.get_current_url()
    title = buy.get_title()

    url_l = current_url.lower()
    ptype_l = str(data["product_type"]).lower().strip()

    try:
        with allure.step("Navigate to listing"):
            home.click_buy_medicines()
            buy.open_nutritional_drinks_and_supplements()

        with allure.step("Apply filter: Product Type → Protein"):
            listing.filter_by_product_type(data["product_type"])

        with allure.step("Verify results are not empty"):
            names = listing.get_visible_product_names()
            listing.logger.info(f"Names after {data["product_type"]} selection: {names}")
            assert len(names) > 0, f"List should not be empty after {data["product_type"]} selection"

        with allure.step("Verify URL and Title reflect product type"):
            import re

            def normalize(text: str) -> str:
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())

            current_url = buy.get_current_url()
            title = buy.get_title()

            term = normalize(data["product_type"])
            url_norm = normalize(current_url)
            title_norm = normalize(title)

            assert term in url_norm or url_norm in term, \
                f"URL should reflect product type '{data['product_type']}' (found: {current_url})"
            assert term in title_norm or title_norm in term, \
                f"Title should reflect product type '{data['product_type']}' (found: {title})"




    except Exception as e:
        listing.capture_screenshot(test_name)
        listing.logger.error(f"TC_03 failed: {e}")
        raise

test_data4 = ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)

@pytest.mark.regression
@pytest.mark.parametrize("data", test_data4)
def test_tc04_filter_by_brand(driver,data,request):
    """
    TC_04: Validate filtering by Brand = Oziva
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    test_name = request.node.name

    try:
        with allure.step("Navigate to listing"):
            home.click_buy_medicines()
            buy.open_nutritional_drinks_and_supplements()
        with allure.step("Apply filter: Product Type → Protein"):
            listing.filter_by_product_type(data["product_type"])

        with allure.step("Apply filter: Brand → oziva"):
            listing.filter_by_type(data["filter_type"],data["filter_option"])

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='J_']/h2[contains(@class, 'O_')]"))
            )

        with allure.step("Verify most or all products reflect the brand"):
            names = listing.get_visible_product_names()
            listing.logger.info(f"Names after brand filter: {names}")
            assert len(names) > 0, "List should not be empty after brand filter"
            cards = [n for n in names if f"{data["filter_option"]}" in n.lower()]
            assert len(cards) >= 1, "At least one visible product should be MuscleBlaze after filter"

        with allure.step("Verify URL and Title reflect filter type"):
            import re

            def normalize(text: str) -> str:
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())

            current_url = buy.get_current_url()
            title = buy.get_title()

            term = normalize(data["filter_option"])
            url_norm = normalize(current_url)
            title_norm = normalize(title)

            assert term in url_norm or url_norm in term, \
                f"URL should reflect  '{data["filter_option"]}' (found: {current_url})"
            assert term in title_norm or title_norm in term, \
                f"Title should reflect  '{data["filter_option"]}' (found: {title})"

    except Exception as e:
        listing.capture_screenshot(test_name)
        listing.logger.error(f"TC_04 failed: {e}")
        raise
