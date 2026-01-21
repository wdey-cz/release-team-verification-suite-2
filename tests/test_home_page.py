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
    def test_home_page_loads(self, sessiondriver, base_url, config_assists):
        """
        Test that the Wikipedia home page loads successfully.

        Args:
            driver: WebDriver instance from fixture
            base_url: Base URL from fixture
        """
        driver = sessiondriver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.sleep_code(4)

        assert wiki_home_page.is_element_present(
            wiki_home_page.SEARCH_BAR, 10
        ), "Search bar should be present on the home page"
        assert "wikipedia" in wiki_home_page.get_page_report()['CURRENT_URL'].lower(), "URL should contain 'wikipedia'"

    @pytest.mark.HomePageSearchRegressionPackage
    def test_search_suggestions(self, sessiondriver, base_url, config_assists):
        # Verify that search suggestions appear when typing in the search bar.
        driver = sessiondriver
        profile = getattr(driver, "_rtvs_profile", None)
        rc = config_assists.get_run_configuration()
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.search("India")
        wiki_home_page.sleep_code(5)

        assert wiki_home_page.suggestion_dropdown_exists(), "Suggestion dropdown should be visible"
        suggestions = wiki_home_page.get_suggestions()
        assert len(suggestions) > 0, "There should be at least one search suggestion"

    @pytest.mark.HomePageSearchRegressionPackage
    def test_click_search_suggestion(self, sessiondriver, base_url, config_assists):
        # Verify that clicking a search suggestion navigates to the correct page.
        driver = sessiondriver
        profile = getattr(driver, "_rtvs_profile", None)
        print("Run ID before setting:", config_assists.run_config.run_id)
        config_assists.run_config.run_id = "HomePageClickSearchSuggestionTest"
        print("Run ID set to:", config_assists.run_config.run_id)
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.search("Australia")
        wiki_home_page.sleep_code(2)
        suggestions_list = wiki_home_page.get_suggestions_from_search_term("Australia")
        for i, suggestion in enumerate(suggestions_list):
            print(f"Suggestion {i}: {suggestion}")
            try:
                wiki_home_page.click_suggestion(i)
                wiki_home_page.sleep_code(2)
                assert "australia" in wiki_home_page.get_page_report()['CURRENT_URL'].lower(), "URL should contain 'Australia' after clicking suggestion"
            except Exception as e:
                print("Error clicking search suggestion:", e)
                traceback.print_exc()
                pytest.fail("Failed to click search suggestion")
            finally:
                wiki_home_page.go_to_homepage()
                wiki_home_page.sleep_code(2)
                wiki_home_page.search("Australia")

    # test_top_languages_displayed: Verify that the top languages are displayed on the home page.
    @pytest.mark.HomePageLanguagesRegressionPackage
    def test_top_languages_displayed(self, sessiondriver, base_url, config_assists):
        driver = sessiondriver
        profile = getattr(driver, "_rtvs_profile", None)
        print("Run ID before setting:", config_assists.run_config.run_id)
        config_assists.run_config.run_id = "HomePageTopLanguagesDisplayTest"
        print("Run ID set to:", config_assists.run_config.run_id)
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()

        assert wiki_home_page.languages_element_exists(), "Languages element should be present on the home page"
        top_languages = wiki_home_page.get_top_languages_list()
        assert len(top_languages) > 0, "There should be at least one top language displayed"

    # test_click_top_language: Verify that clicking a top language navigates to the correct language page.
    # Choose 4 languages at random from the top languages and click them one by one to verify navigation.
    # Return to homepage after each click and validation. 2 seconds sleep after each navigation to allow page to load.
    @pytest.mark.HomePageLanguagesRegressionPackage
    def test_click_top_language(self, sessiondriver, base_url, config_assists):
        driver = sessiondriver
        profile = getattr(driver, "_rtvs_profile", None)
        print("Run ID before setting:", config_assists.run_config.run_id)
        config_assists.run_config.run_id = "HomePageClickTopLanguageTest"
        print("Run ID set to:", config_assists.run_config.run_id)
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()

        top_languages = wiki_home_page.get_top_languages_list()
        languages_to_test = top_languages[:4]  # Select first 4 languages for testing

        for language in languages_to_test:
            try:
                wiki_home_page.click_language_by_name(language)
                wiki_home_page.sleep_code(2)
                assert wiki_home_page.wiki_logo_exists(), f"New Page should contain the wikipedia logo element"
                wiki_home_page.go_to_homepage()
                wiki_home_page.sleep_code(2)
            except Exception as e:
                print(f"Error clicking top language '{language}':", e)
                traceback.print_exc()
                pytest.fail(f"Failed to click top language '{language}'")




