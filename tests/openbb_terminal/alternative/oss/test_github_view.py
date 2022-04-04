# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.oss import github_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_star_history(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.alternative.oss.github_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    github_view.display_star_history(repo="openbb-finance/openbbterminal")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_top_repos(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.alternative.oss.github_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    github_view.display_top_repos(sortby="stars", categories="", limit=10)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_repo_summary(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.alternative.oss.github_view.export_data")

    github_view.display_repo_summary(
        repo="openbb-finance/openbbterminal",
    )
