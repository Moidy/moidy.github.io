import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Override with SITE_URL env var to test a different environment
BASE_URL = os.environ.get("SITE_URL", "https://moidy.github.io")


@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()


@pytest.fixture
def page(driver):
    """Navigate to the homepage before each test."""
    driver.get(BASE_URL)
    return driver
