from core.driver_factory import WebDriverFactory
from pages.wiki_homepage import WikiHomePage
from multiprocessing import Pool, Lock

def search_term(term):
    print("Initializing WebDriver...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True)
    try:
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        print("Navigated to Wikipedia homepage successfully.")
        wiki_home_page.click_search_bar()
        wiki_home_page.search(term)
        wiki_home_page.sleep_code(3)
        print("Search action performed successfully.")
        print(wiki_home_page.get_suggestions())
        wiki_home_page.click_suggestion(2)
        wiki_home_page.sleep_code(2)
        wiki_home_page.driver.refresh()
        wiki_home_page.sleep_code(2)
    except Exception as e:
        print(f"Error during Wikipedia navigation test: {e}")
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)


def check_languages():
    print("Initializing WebDriver for language check...")
    driver, profile = WebDriverFactory.get_driver(use_chrome_profile=True)
    try:
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        print("Navigated to Wikipedia homepage successfully.")
        if wiki_home_page.languages_element_exists():
            lan_list = wiki_home_page.get_top_languages_list()
            wiki_home_page.click_language_by_name(lan_list[2])
            wiki_home_page.sleep_code(2)
        else:
            print("Languages element not found on the homepage.")
    except Exception as e:
        print(f"Error during language check: {e}")
    finally:
        driver.quit()
        WebDriverFactory.release_driver_from_profile(browser_name="chrome", profile_name=profile)



def search_a_set_via_multiprocessing(list_of_terms):
    # call search_term in parallel for each term in list_of_terms
    with Pool(processes=len(list_of_terms)) as pool:
        pool.map(search_term, list_of_terms)









if __name__ == "__main__":
    #search_a_set_via_multiprocessing(["India", "USA", "UK", "Germany"])
    #search_term("India")
    check_languages()
