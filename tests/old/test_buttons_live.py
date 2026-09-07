from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import pytest
import time

@pytest.fixture
def driver2():
    opts = Options()
    #opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox") #argument to run Chrome in a sandboxed environment, which can help improve security and stability.
    opts.add_argument("--disable-dev-shm-usage") # This argument is used to disable the use of /dev/shm (shared memory) in Chrome. In some environments, especially in Docker containers, /dev/shm may have limited space, which can cause issues with Chrome. Disabling it can help avoid such problems.
    opts.add_argument("--window-size=3840,2160") # This argument sets the initial window size of the Chrome browser to 3840 pixels wide and 2160 pixels tall. This can be useful for testing how a web application behaves at different screen resolutions, especially for high-resolution displays.
    # fullscreen = True
    opts.add_argument("--start-maximized") # This argument tells Chrome to start in a maximized window state. It ensures that the browser window takes up the entire screen space available, which can be useful for testing web applications in a full-screen environment.
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()

def wait_for(driver, css_selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )

def explicit_wait(driver, css_selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
    )

def explicit_wait_xpath(driver, xpath_selector, timeout=10):
    """ Wait for an element to be visible using an XPath selector.
    
    Returns the WebElement once it is visible, or raises a TimeoutException if the element does not become visible within the specified timeout.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath_selector))
    )

def wait_till_visible(driver, css_selector, timeout=10):
    """ Wait for an element to be visible using a CSS selector.
    
    Returns the WebElement once it is visible, or raises a TimeoutException if the element does not become visible within the specified timeout."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def test_hero_cta_button_points_to_projects(driver2):
    driver2.get("https://moidy.github.io")
    wait_for(driver2, ".hero .btn-primary")
    driver2.implicitly_wait(10)
    driver2.find_element(By.CSS_SELECTOR, ".hero .btn-primary").click()
    explicit_wait(driver2, "article.project-card")
    assert "projects" in driver2.current_url
    button_element = "article.project-card:nth-child(1) > div:nth-child(2) > a:nth-child(6)"
    explicit_wait(driver2, button_element)
    driver2.find_element(By.CSS_SELECTOR, button_element).click()
    assert "sharon" in driver2.current_url
    wait_till_visible(driver2, ".post-hero > img:nth-child(1)", timeout=10)
    explicit_wait_xpath(driver2, "/html/body/article/div/div[1]/img", timeout=10)
    #wait for the page text to fully load
    assert "Sharon is a fully autonomous AI VTuber designed to run live on a Twitch stream." in driver2.page_source
    assert "https://moidy.github.io/projects/sharon/" == driver2.current_url


## test of sending keys to amazon search bar
def test_amazon_search(driver2):    
    driver2.get("https://www.amazon.com")
    wait_for(driver2, "#twotabsearchtextbox")
    search_box: WebElement = driver2.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys("laptop")
    search_box.submit()
    wait_for(driver2, ".s-main-slot")
    assert "laptop" in driver2.current_url
    time.sleep(10)  # Wait for the page to load completely

# selenium test with paramatarized input for search terms
@pytest.mark.parametrize("search_term", ["laptop", "headphones", "smartphone"])
def test_amazon_search_param(driver2, search_term):    
    driver2.get("https://www.amazon.com")
    wait_for(driver2, "#twotabsearchtextbox")
    search_box: WebElement = driver2.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys(search_term)
    search_box.submit()
    wait_for(driver2, ".s-main-slot")
    assert search_term in driver2.current_url
