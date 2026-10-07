import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--llm_assert",
        action="store",
        default="base",
        choices=["yes",'no'],
        help="choose an assert model"
    )


@pytest.fixture(scope="module")
def llm__assert(request):
    return request.config.getoption("--llm_assert")
