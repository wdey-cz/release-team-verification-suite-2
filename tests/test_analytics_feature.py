import pytest


@pytest.mark.CozevaComboPack1
@pytest.mark.AnalyticsTestPackage
class TestAnalytics:

    def test_quality_overview_wb(self, logged_in_driver, base_url, config_assists):
        sit = 1