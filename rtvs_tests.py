from core.driver_factory import WebDriverFactory
from pages.cozeva_login_page import CozevaLoginPage
from core.config import Config
from multiprocessing import Pool

def login_splash_test():
    print("Initializing WebDriver...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True)
    try:
        login_page = CozevaLoginPage(driver)
        login_page.go_to_login_page(Config.get_base_url())
    except Exception as e:
        print(f"Error during Wikipedia navigation test: {e}")
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)

if __name__ == "__main__":
    login_splash_test()

