from xmlrpc.client import boolean
# tests/test_end_to_end.py
import pytest
import allure
import time
import itertools
from pages.homepage import HomePage
from pages.buy_medicines_page import BuyMedicinePage
from pages.product_listing_page import ProductListingPage
from utils.excel_reader import ExcelReader
from pages.product_detail_page import ProductDetailPage
from pages.Cartpage import CartPage



test_data_e2e_1= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
@pytest.mark.parametrize("data", test_data_e2e_1)
@pytest.mark.e2e
def test_t1_e2e_knownitem(driver, data,request):
    """
    T1_E2E_KNOWNITEM: Validate end-to-end process for a known item

    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    cart = CartPage(driver)
    test_name = request.node.name


    try:
        with allure.step("Open buy medicines page"):
            home.click_buy_medicines()
        with allure.step("Open 'Nutritional Drinks & Supplements'"):
            buy.open_nutritional_drinks_and_supplements()
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
                    f"Title should reflect '{data['known_item']}' (found: {title})"


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
                f"URL should reflect  '{data['delivery_term']}' (found: {current_url})"
            assert term in title_norm or title_norm in term, \
                f"Title should reflect  '{data['delivery_term']}' (found: {title})"

        with allure.step(f"Select delivery slot: {data["del_type"]} / {data["date_label"]} / {data["time_label"]}"):
            with allure.step(f"Select delivery slot: {data["del_type"]} / {data["date_label"]} / {data["time_label"]}"):
                if (data["del_type"] == 'Express Delivery'):
                    cart.select_preferred_slot(data["del_type"])
                else:
                    cart.select_preferred_slot_time(data["del_type"], data["date_label"], data["time_label"])
            # cart.select_preferred_slot(data["del_type"])
            # #cart.select_preferred_slot_time(del_type, date_label, time_label)
            cart.final_checkout(data["payment_type"])
            with allure.step("Verify URL and Title reflect payment page"):
                import re

                def normalize(text: str) -> str:
                    return re.sub(r'[^a-z0-9]', '', (text or '').lower())

                current_url = buy.get_current_url()
                title = buy.get_title()

                term = normalize(data["pay_term"])
                url_norm = normalize(current_url)
                title_norm = normalize(title)

                assert term in url_norm or url_norm in term, \
                    f"URL should reflect  '{data['pay_term']}' (found: {current_url})"
                assert term in title_norm or title_norm in term, \
                    f"Title should reflect  '{data['pay_term']}' (found: {title})"
            cart.logger.info(f"Successfully reached payment page and selected payment option")


        # If UI exposes a 'selected' state, you can add a direct assertion here.
        assert True, "Error occurred"

    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_t1_e2e_knownitem failed: {e}")
        raise




test_data_e2e1= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_1"
)
test_data_e2e2= ExcelReader.read_excel(
    file_name="test_data_sprint.xlsx",
    sheet_name="test_2"
)
cases = list(itertools.product(test_data_e2e1, test_data_e2e2))
@pytest.mark.e2e
@pytest.mark.parametrize(("data","dataa"), cases)
def test_t2_e2e_anyitem(driver, data,dataa,request):
    """
    TC_E2E_ANYITEM: Validate end-to-end process for any item
    """
    home = HomePage(driver)
    buy = BuyMedicinePage(driver)
    listing = ProductListingPage(driver)
    pdp = ProductDetailPage(driver)
    cart = CartPage(driver)
    test_name = request.node.name

    try:
     with allure.step("Navigate to listing"):
        home.click_buy_medicines()
        buy.open_nutritional_drinks_and_supplements()
     with allure.step("Apply filter: Product Type → Protein"):
        listing.filter_by_product_type(data["product_type"])

     elements = driver.find_elements(*listing.PRODUCT_NAMES)
     title_element = elements[int(dataa["prod_num"])-1].text
     time.sleep(5)
     with allure.step("Select specified product number"):
        listing.select_product(dataa["prod_num"])
        time.sleep(5)

     with allure.step("Verify URL and Title reflect product type"):
         import re

         def normalize(text: str) -> str:
             return re.sub(r'[^a-z0-9]', '', (text or '').lower())

         title = buy.get_title()

         term = normalize(f"{title_element}")

         title_norm = normalize(title)


         assert term in title_norm or title_norm in term, \
             f"Title should reflect product type '{title_element}' (found: {title})"
     pdp.add_to_cart(dataa["qty"])
     pdp.open_cart()

     with allure.step(f"Change cart quantity to {dataa["final_qty"]} "):
       if int(dataa["final_qty"])>1 :
         skip= 1
       name=pdp.get_product_title()
       cart.change_quantity(name, dataa["final_qty"])

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
             f"URL should reflect  '{data['delivery_term']}' (found: {current_url})"
         assert term in title_norm or title_norm in term, \
             f"Title should reflect  '{data['delivery_term']}' (found: {title})"

     with allure.step(f"Select delivery slot: {dataa["del_type"]} / {data["date_label"]} / {data["time_label"]}"):
        if skip==1:
         pass
        elif dataa["del_type"] == 'Express Delivery':
         cart.select_preferred_slot(data["del_type"])
        elif dataa["del_type"] == 'Standard Delivery':
            cart.select_preferred_slot(data["del_type"])
        else:
         cart.select_preferred_slot_time(dataa["del_type"], data["date_label"], data["time_label"])
     cart.final_checkout(data["payment_type"])
     with allure.step("Verify URL and Title reflect payment page"):
         import re

         def normalize(text: str) -> str:
             return re.sub(r'[^a-z0-9]', '', (text or '').lower())

         current_url = buy.get_current_url()
         title = buy.get_title()

         term = normalize(data["pay_term"])
         url_norm = normalize(current_url)
         title_norm = normalize(title)

         assert term in url_norm or url_norm in term, \
             f"URL should reflect '{data['pay_term']}' (found: {current_url})"
         assert term in title_norm or title_norm in term, \
             f"Title should reflect '{data['pay_term']}' (found: {title})"
     cart.logger.info(f"Successfully reached payment page and selected payment option")

    except Exception as e:
        cart.capture_screenshot(test_name)
        cart.logger.error(f"TC_t2_e2e_anyitem failed: {e}")
        raise



