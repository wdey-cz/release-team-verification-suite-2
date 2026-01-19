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
        driver, profile = sessiondriver
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()

        assert wiki_home_page.is_element_present(
            wiki_home_page.SEARCH_BAR, 10
        ), "Search bar should be present on the home page"
        assert "wikipedia" in wiki_home_page.get_page_report()['CURRENT_URL'].lower(), "URL should contain 'wikipedia'"

    @pytest.mark.HomePageSearchRegressionPackage
    def test_search_suggestions(self, sessiondriver, base_url, config_assists):
        # Verify that search suggestions appear when typing in the search bar.
        driver, profile = sessiondriver
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.click_search_bar()
        wiki_home_page.search("India")
        wiki_home_page.sleep_code(2)

        assert wiki_home_page.suggestion_dropdown_exists(), "Suggestion dropdown should be visible"
        suggestions = wiki_home_page.get_suggestions()
        assert len(suggestions) > 0, "There should be at least one search suggestion"

    @pytest.mark.HomePageSearchRegressionPackage
    def test_click_search_suggestion(self, sessiondriver, base_url, config_assists):
        # Verify that clicking a search suggestion navigates to the correct page.
        driver, profile = sessiondriver
        wiki_home_page = WikiHomePage(driver)
        wiki_home_page.go_to_homepage()
        wiki_home_page.click_search_bar()
        wiki_home_page.search("India")
        wiki_home_page.sleep_code(2)

        try:
            wiki_home_page.click_suggestion(0)
            wiki_home_page.sleep_code(2)
            assert "india" in wiki_home_page.get_page_report()['CURRENT_URL'].lower(), "URL should contain 'India' after clicking suggestion"
        except Exception as e:
            print("Error clicking search suggestion:", e)
            traceback.print_exc()
            pytest.fail("Failed to click search suggestion")



