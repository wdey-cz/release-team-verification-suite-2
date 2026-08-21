"""
HCC V28 data integrity validation package.

Run via Controller GUI (DATA category) or:
  pytest -m HCCV28ValidationPackage --client-id=<id> --user-role="Cozeva Support"

Optional env vars (defaults match the original standalone script):
  RTVS_HCC_YEAR, RTVS_HCC_MEASURES, RTVS_HCC_LOB,
  RTVS_HCC_PROVIDER_COUNT, RTVS_HCC_PATIENT_COUNT, RTVS_HCC_PATIENT_DASHBOARD,
  RTVS_HCC_FLOAT_TOLERANCE, RTVS_HCC_PERF_TOLERANCE
"""
from __future__ import annotations

import traceback
from pathlib import Path

import pytest

from core.base_page import HeaderNavBar
from core.config import Config
from pages.cozeva_hcc_v28_page import CozevaHCCV28Page, load_hcc_settings
from pages.cozeva_registries_page import CozevaRegistriesPage


@pytest.mark.HCCV28ValidationPackage
class TestHCCV28Validation:

    def test_hcc_v28_validation(self, logged_in_driver, config_assists):
        """
        Feature - D_HCC_V28
        Validates selected HCC V28 measures across Support Registry, Practice Registry,
        Provider MSPL (domain / performance / network / export scores), and optionally
        Patient Dashboard RAF ribbons. Produces a color-coded Excel report under REPORTS_DIR.
        """
        driver = logged_in_driver
        rc = config_assists.get_run_configuration()
        failed_cases = 0

        if not rc.client_id:
            config_assists.add_log_update(
                message="client_id is required for HCC V28 DATA package (select a customer in Controller).",
                driver=driver,
                status="FAILED",
            )
            pytest.fail("client_id is required for HCCV28ValidationPackage")

        user_role = rc.user_role or ""
        if user_role and user_role not in [
            "Cozeva Support",
            "Customer Support",
            "Regional Support",
            "Limited Cozeva Support",
        ]:
            config_assists.add_log_update(
                message=f"User role {user_role} is not in scope for HCC V28 validation.",
                driver=driver,
            )
            pytest.skip(f"User role {user_role} is not in scope for this test.")

        try:
            rc.base_landing_url = driver.current_url

            download_dir = Config.RTVS_DOWNLOADS_DIR / (rc.lane_id or "")
            download_dir.mkdir(parents=True, exist_ok=True)
            report_dir = Config.REPORTS_DIR / (rc.run_id or "adhoc_hcc_v28")
            report_dir.mkdir(parents=True, exist_ok=True)

            settings = load_hcc_settings(
                csv_download_dir=download_dir,
                report_dir=report_dir,
                lane_id=rc.lane_id,
            )
            config_assists.add_log_update(
                message=(
                    f"HCC settings loaded | year={settings.year} lob={settings.selected_lob or 'ALL'} "
                    f"measures={settings.selected_checklist} providers={settings.provider_count} "
                    f"patients={settings.patient_count} dashboard={settings.patient_dashboard} "
                    f"csv={settings.csv_download_dir} report={settings.report_dir}"
                ),
                driver=driver,
                status="IN_PROGRESS",
            )

            header_nav = HeaderNavBar(driver)
            header_nav.click_sidebar_entry("Registries")
            registries_page = CozevaRegistriesPage(driver)
            if not registries_page.is_registries_page_opened():
                config_assists.add_log_failed(
                    message="Failed to open Support Registries for HCC V28 validation",
                    driver=driver,
                )
                pytest.fail("Support Registries page did not open")

            config_assists.add_log_heartbeat(
                "Starting HCC V28 validation",
                driver=driver,
                status="STARTED",
            )

            hcc_page = CozevaHCCV28Page(driver, settings=settings)
            report_path = hcc_page.run_hcc_v28_validation(
                customer_value=str(rc.client_id),
                config_assists=config_assists,
            )

            if not Path(report_path).exists():
                failed_cases += 1
                config_assists.add_log_test_case(
                    message="HCC V28 Excel report generation",
                    test_case_id="HCC_V28_99",
                    status="FAILED",
                    driver=driver,
                    comment=f"Expected report missing: {report_path}",
                )
            else:
                config_assists.add_log_test_case(
                    message="HCC V28 Excel report generation",
                    test_case_id="HCC_V28_99",
                    status="PASSED",
                    driver=driver,
                    comment=f"Report saved: {report_path}",
                )

            config_assists.add_log_heartbeat(
                "Finished HCC V28 validation",
                driver=driver,
                status="FINISHED",
            )

            if failed_cases:
                pytest.fail(f"HCC V28 validation finished with {failed_cases} failed case(s)")

        except Exception as e:
            traceback.print_exc()
            config_assists.add_log_error(
                message=f"HCC V28 validation crashed: {e}",
                driver=driver,
            )
            raise
