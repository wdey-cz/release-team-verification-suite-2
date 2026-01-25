import pytest
from pages.wiki_homepage import WikiHomePage

import traceback





@pytest.mark.smoke
@pytest.mark.HomePageComboPack1
class TestHomePage:
    """Test cases for Wikipedia home page functionality.
    Test cases:
    1. test_home_page_loads: Verify that the Wikipedia home page loads successfully.
    2. test_search_suggestions: Verify that search suggestions appear when typing in the search bar.
    3. test_click_search_suggestion: Verify that clicking a search suggestion navigates to the correct page.
    4. test_top_languages_displayed: Verify that the top languages are displayed on the home page.
    5. test_click_top_language: Verify that clicking a top language navigates to the correct language page.

    """


    @pytest.mark.HomePageSearchRegressionPackage
    @pytest.mark.HomePageLanguagesRegressionPackage
    def test_home_page_loads(self, session_driver, base_url, config_assists):
        """
        Test that the Wikipedia home page loads successfully.

        Args:
            session_driver: WebDriver instance from fixture
            base_url: Base URL from fixture
        """

        # Test Function setup
        driver = session_driver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.sleep_code(4)
        config_assists.add_log_update(message=f"Navigated to {wiki_home_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases", driver=driver)

        # Test Case 1: Verify that the search bar is present on the home page.
        config_assists.add_log_heartbeat("Starting the Search Bar Element Check", driver=driver)
        if wiki_home_page.is_element_present(wiki_home_page.SEARCH_BAR, 10):
            config_assists.add_log_test_case(message="Checking that the search bar is present on the home page", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that the search bar is present on the home page", status='FAILED', driver=driver)
            failed_cases += 1


        # Test Case 2: Verify that the page URL contains 'wikipedia'.
        config_assists.add_log_heartbeat("Starting the URL Check", driver=driver)
        if "wikipedia" in wiki_home_page.get_page_report()['CURRENT_URL'].lower():
            config_assists.add_log_test_case(message="Checking that the page URL contains 'wikipedia'", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that the page URL contains 'wikipedia'", status='FAILED', driver=driver)
            failed_cases += 1

        if failed_cases == 0:
            config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
        else:
            config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)


        # Test functions will have only one assert. This assert will check  if failed cases is
        assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."



    @pytest.mark.HomePageSearchRegressionPackage
    @pytest.mark.parametrize("search_term", ["India", "Australia"])
    def test_search_suggestions(self, session_driver, base_url, config_assists, search_term):
        # Verify that search suggestions appear when typing in the search bar.

        # Test Function setup
        driver = session_driver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        config_assists.add_log_update(message=f"Navigated to {wiki_home_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases", driver=driver)

        # Test Case 1: Verify that search suggestions appear when typing in the search bar.
        config_assists.add_log_heartbeat("Starting the Search bar Check", driver=driver)
        wiki_home_page.search(search_term)
        wiki_home_page.sleep_code(3)
        config_assists.add_log_update(f"Searched {search_term}", driver=driver)

        if wiki_home_page.suggestion_dropdown_exists():
            config_assists.add_log_test_case(message="Checking that search suggestions appear when typing in the search bar", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that search suggestions appear when typing in the search bar", status='FAILED', driver=driver)
            failed_cases += 1

        # Test Case 2: Verify that at least one search suggestion is displayed.
        config_assists.add_log_heartbeat("Starting at least one suggestion check", driver=driver)
        suggestions = wiki_home_page.get_suggestions()
        if len(suggestions) > 0:
            config_assists.add_log_test_case(message="Checking that at least one search suggestion is displayed", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that at least one search suggestion is displayed", status='FAILED', driver=driver)
            failed_cases += 1

        if failed_cases == 0:
            config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
        else:
            config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)
        # Test functions will have only one assert. This assert will check  if failed cases is
        assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."

    @pytest.mark.HomePageSearchRegressionPackage
    def test_click_search_suggestion(self, session_driver, base_url, config_assists):
        # Verify that clicking a search suggestion navigates to the correct page.
        # Test Function setup
        driver = session_driver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        config_assists.add_log_update(message=f"Navigated to {wiki_home_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases", driver=driver)

        # Test Case: Click each suggestion for the search term "Australia" and verify navigation.
        config_assists.add_log_heartbeat("Starting the suggestions click check", driver=driver)
        wiki_home_page.search("Australia")
        wiki_home_page.sleep_code(2)
        config_assists.add_log_update("Starting suggestion click loop for Australia", driver=driver)
        suggestions_list = wiki_home_page.get_suggestions_from_search_term("Australia")
        for i, suggestion in enumerate(suggestions_list):
            print(f"Suggestion {i}: {suggestion}")
            try:
                wiki_home_page.click_suggestion(i)
                wiki_home_page.sleep_code(2)
                if "australia" in wiki_home_page.get_page_report()['CURRENT_URL'].lower():
                    config_assists.add_log_test_case(message=f"Clicking suggestion '{suggestion}' navigates to correct page", status='PASSED', driver=driver)
                else:
                    config_assists.add_log_test_case(message=f"Clicking suggestion '{suggestion}' navigates to correct page", status='FAILED', driver=driver)
                    failed_cases += 1
            except Exception as e:
                print("Error clicking search suggestion:", e)
                traceback.print_exc()
                config_assists.add_log_test_case(message=f"Error clicking search suggestion '{suggestion}'", status='FAILED', driver=driver)
                pytest.fail("Failed to click search suggestion")
            finally:
                wiki_home_page.go_to_homepage()
                wiki_home_page.sleep_code(2)
                wiki_home_page.search("Australia")

        if failed_cases == 0:
            config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
        else:
            config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)
        # Test functions will have only one assert. This assert will check  if failed cases is
        assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."

    # test_top_languages_displayed: Verify that the top languages are displayed on the home page.
    @pytest.mark.HomePageLanguagesRegressionPackage
    def test_top_languages_displayed(self, session_driver, base_url, config_assists):

        # Test Function setup
        driver = session_driver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        page_title = wiki_home_page.get_page_report()['CURRENT_TITLE']
        config_assists.add_log_update(message=f"Navigated to {page_title} for " + __name__ + " test cases", driver=driver)


        # Test_case 1 : Verify that the top languages container is visible
        config_assists.add_log_heartbeat("Starting the Languages Element Check", driver=driver)
        if wiki_home_page.languages_element_exists():
            config_assists.add_log_test_case(message="Checking that the top languages container is visible", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that the top languages container is visible", status='FAILED', driver=driver)
            failed_cases += 1

        # Test_case 2 : Verify that at least one top language is displayed
        config_assists.add_log_heartbeat(message="Starting at least one top language check", driver=driver)
        top_languages = wiki_home_page.get_top_languages_list()
        if len(top_languages) > 0:
            config_assists.add_log_test_case(message="Checking that at least one top language is displayed", status='PASSED', driver=driver)
        else:
            config_assists.add_log_test_case(message="Checking that at least one top language is displayed", status='FAILED', driver=driver)
            failed_cases += 1

        if failed_cases == 0:
            config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
        else:
            config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)
        # Test functions will have only one assert. This assert will check  if failed cases is < 1 , if so assert failurte that thius test has failed.
        assert failed_cases < 1, f"{failed_cases} test cases have failed in this test."

    # test_click_top_language: Verify that clicking a top language navigates to the correct language page.
    # Choose 4 languages at random from the top languages and click them one by one to verify navigation.
    # Return to homepage after each click and validation. 2 seconds sleep after each navigation to allow page to load.
    @pytest.mark.HomePageLanguagesRegressionPackage
    def test_click_top_language(self, session_driver, base_url, config_assists):

        # Test Function setup
        driver = session_driver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        config_assists.add_log_update(message=f"Navigated to {wiki_home_page.get_page_report()['CURRENT_TITLE']} for " + rc.test_name + " test cases", driver=driver)

        config_assists.add_log_heartbeat("Starting the Languages Element Check", driver=driver)
        top_languages = wiki_home_page.get_top_languages_list()
        languages_to_test = top_languages[:3]  # Select first 4 languages for testing

        for language in languages_to_test:
            try:
                wiki_home_page.click_language_by_name(language)
                wiki_home_page.sleep_code(2)
                if wiki_home_page.wiki_logo_exists():
                    config_assists.add_log_test_case(message=f"Clicking top language '{language}' navigates to correct page", status='PASSED', driver=driver)
                else:
                    config_assists.add_log_test_case(message=f"Clicking top language '{language}' navigates to correct page", status='FAILED', driver=driver)
                    failed_cases += 1
            except Exception as e:
                print(f"Error clicking top language '{language}':", e)
                traceback.print_exc()
                pytest.fail(f"Failed to click top language '{language}'")
            finally:
                wiki_home_page.go_to_homepage()
                wiki_home_page.sleep_code(2)

        if failed_cases == 0:
            config_assists.add_log_update("All test cases passed for " + rc.test_name, driver=driver)
        else:
            config_assists.add_log_update(f"{failed_cases} test cases failed for " + rc.test_name, driver=driver)
        # Test functions will have only one assert. This assert will check  if failed cases is
        assert failed_cases < 1, f"{failed_cases} test cases have failed in this test: {rc.test_name}."





