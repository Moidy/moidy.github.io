"""
Advanced Selenium Test Examples for Interview Practice

This file contains various advanced Selenium testing patterns and techniques:
- Page Object Model (POM)
- Multiple window/tab handling
- iFrame interactions
- Alert/popup handling
- Drag and drop
- Hover actions
- Dynamic waits and conditions
- JavaScript execution
- Screenshot capture
- Cookie management
- Select/dropdown handling
- File upload
- Browser logs
- Custom expected conditions
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest
import time
from datetime import datetime
import os


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def driver():
    """Standard driver fixture with common options"""
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    # Uncomment for headless mode
    # opts.add_argument("--headless=new")
    
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_page_load_timeout(30)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture
def driver_with_logs(driver):
    """Driver fixture that enables browser log capture"""
    driver.get("about:blank")
    yield driver
    # Print browser console logs after test
    for entry in driver.get_log('browser'):
        print(entry)


# ============================================================================
# PAGE OBJECT MODEL EXAMPLE
# ============================================================================

class GoogleSearchPage:
    """Page Object for Google Search - demonstrates POM pattern"""
    
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://www.google.com"
        
    # Locators
    SEARCH_BOX = (By.NAME, "q")
    SEARCH_BUTTON = (By.NAME, "btnK")
    RESULTS_STATS = (By.ID, "result-stats")
    FIRST_RESULT = (By.CSS_SELECTOR, "div.g")
    
    def open(self):
        """Navigate to Google homepage"""
        self.driver.get(self.url)
        return self
    
    def search(self, query):
        """Perform a search"""
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.SEARCH_BOX)
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        return self
    
    def get_results_count(self):
        """Get the number of search results"""
        stats = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.RESULTS_STATS)
        )
        return stats.text
    
    def get_first_result_text(self):
        """Get text from first search result"""
        first_result = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.FIRST_RESULT)
        )
        return first_result.text


def test_page_object_model(driver):
    """Demonstrates Page Object Model pattern"""
    google_page = GoogleSearchPage(driver)
    google_page.open().search("Selenium WebDriver")
    
    results = google_page.get_results_count()
    assert "results" in results.lower()
    
    first_result = google_page.get_first_result_text()
    assert len(first_result) > 0


# ============================================================================
# MULTIPLE WINDOWS/TABS
# ============================================================================

def test_handle_multiple_windows(driver):
    """Demonstrates switching between multiple windows/tabs"""
    driver.get("https://www.selenium.dev/documentation/")
    
    # Store original window handle
    original_window = driver.current_window_handle
    assert len(driver.window_handles) == 1
    
    # Open a new tab using JavaScript
    driver.execute_script("window.open('https://www.google.com', '_blank');")
    
    # Wait for new window/tab
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    
    # Switch to new window
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
    
    # Verify we're on Google
    assert "google" in driver.current_url.lower()
    
    # Close current tab and switch back
    driver.close()
    driver.switch_to.window(original_window)
    
    # Verify we're back on Selenium docs
    assert "selenium" in driver.current_url.lower()


def test_window_handles_with_actions(driver):
    """Advanced window handling with multiple operations"""
    driver.get("https://www.selenium.dev")
    
    # Get all links on the page
    links = driver.find_elements(By.TAG_NAME, "a")[:3]  # Get first 3 links
    
    # Open first valid link in new tab
    for link in links:
        href = link.get_attribute("href")
        if href and href.startswith("http"):
            # Ctrl+Click to open in new tab (Cmd+Click on Mac)
            ActionChains(driver).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
            break
    
    # Wait and switch to new tab
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1])
    
    # Perform action in new tab
    print(f"New tab URL: {driver.current_url}")
    
    # Switch back to original tab
    driver.switch_to.window(driver.window_handles[0])


# ============================================================================
# IFRAME HANDLING
# ============================================================================

def test_iframe_interaction(driver):
    """Demonstrates working with iframes"""
    # Using a demo site with iframes
    driver.get("https://the-internet.herokuapp.com/iframe")
    
    # Switch to iframe by element
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mce_0_ifr"))
    )
    driver.switch_to.frame(iframe)
    
    # Interact with content inside iframe
    editor = driver.find_element(By.ID, "tinymce")
    editor.clear()
    editor.send_keys("Testing iframe interaction!")
    
    # Switch back to default content
    driver.switch_to.default_content()
    
    # Verify we're back in main content
    heading = driver.find_element(By.TAG_NAME, "h3")
    assert "Editor" in heading.text


def test_nested_iframes(driver):
    """Handling nested iframes"""
    driver.get("https://the-internet.herokuapp.com/nested_frames")
    
    # Switch to top frame
    driver.switch_to.frame("frame-top")
    
    # Switch to middle frame (nested)
    driver.switch_to.frame("frame-middle")
    
    # Get content from nested frame
    content = driver.find_element(By.ID, "content")
    assert "MIDDLE" in content.text
    
    # Switch back to top level
    driver.switch_to.default_content()


# ============================================================================
# ALERT/POPUP HANDLING
# ============================================================================

def test_javascript_alerts(driver):
    """Demonstrates handling JavaScript alerts"""
    driver.get("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Test basic alert
    driver.find_element(By.XPATH, "//button[text()='Click for JS Alert']").click()
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert_text = alert.text
    assert "JS Alert" in alert_text
    alert.accept()
    
    # Verify result
    result = driver.find_element(By.ID, "result")
    assert "successfully" in result.text.lower()


def test_javascript_confirm(driver):
    """Demonstrates handling JavaScript confirm dialogs"""
    driver.get("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Test confirm - accept
    driver.find_element(By.XPATH, "//button[text()='Click for JS Confirm']").click()
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert.accept()
    result = driver.find_element(By.ID, "result")
    assert "Ok" in result.text
    
    # Test confirm - dismiss
    driver.find_element(By.XPATH, "//button[text()='Click for JS Confirm']").click()
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert.dismiss()
    result = driver.find_element(By.ID, "result")
    assert "Cancel" in result.text


def test_javascript_prompt(driver):
    """Demonstrates handling JavaScript prompts with input"""
    driver.get("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Test prompt with input
    test_input = "Selenium Test Input"
    driver.find_element(By.XPATH, "//button[text()='Click for JS Prompt']").click()
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert.send_keys(test_input)
    alert.accept()
    
    result = driver.find_element(By.ID, "result")
    assert test_input in result.text


# ============================================================================
# DRAG AND DROP
# ============================================================================

def test_drag_and_drop(driver):
    """Demonstrates drag and drop functionality"""
    driver.get("https://the-internet.herokuapp.com/drag_and_drop")
    
    source = driver.find_element(By.ID, "column-a")
    target = driver.find_element(By.ID, "column-b")
    
    # Get initial text
    initial_source_text = source.text
    initial_target_text = target.text
    
    # Perform drag and drop
    ActionChains(driver).drag_and_drop(source, target).perform()
    
    time.sleep(1)  # Wait for animation
    
    # Verify elements swapped
    assert source.text == initial_target_text
    assert target.text == initial_source_text


def test_drag_and_drop_by_offset(driver):
    """Demonstrates drag and drop by pixel offset"""
    driver.get("https://jqueryui.com/draggable/")
    
    # Switch to iframe containing the draggable element
    driver.switch_to.frame(0)
    
    draggable = driver.find_element(By.ID, "draggable")
    
    # Get initial position
    initial_location = draggable.location
    
    # Drag by offset
    ActionChains(driver).drag_and_drop_by_offset(draggable, 100, 50).perform()
    
    time.sleep(1)
    
    # Verify position changed
    new_location = draggable.location
    assert new_location['x'] != initial_location['x']
    assert new_location['y'] != initial_location['y']
    
    driver.switch_to.default_content()


# ============================================================================
# HOVER/MOUSE ACTIONS
# ============================================================================

def test_hover_action(driver):
    """Demonstrates hover/mouseover actions"""
    driver.get("https://the-internet.herokuapp.com/hovers")
    
    # Find first figure
    figure = driver.find_element(By.CSS_SELECTOR, ".figure")
    
    # Hover over the figure
    ActionChains(driver).move_to_element(figure).perform()
    
    # Wait for caption to appear
    caption = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".figcaption"))
    )
    
    assert caption.is_displayed()
    assert "user1" in caption.text.lower()


def test_complex_action_chains(driver):
    """Demonstrates complex action chains"""
    driver.get("https://www.selenium.dev")
    
    # Complex action: move, click, hold, release
    search_area = driver.find_element(By.TAG_NAME, "body")
    
    actions = ActionChains(driver)
    actions.move_to_element(search_area)
    actions.click()
    actions.key_down(Keys.CONTROL)
    actions.send_keys("a")
    actions.key_up(Keys.CONTROL)
    actions.perform()
    
    # Right-click context menu
    actions = ActionChains(driver)
    actions.context_click(search_area).perform()
    
    time.sleep(1)


# ============================================================================
# SELECT/DROPDOWN HANDLING
# ============================================================================

def test_select_dropdown(driver):
    """Demonstrates working with select dropdowns"""
    driver.get("https://the-internet.herokuapp.com/dropdown")
    
    dropdown_element = driver.find_element(By.ID, "dropdown")
    select = Select(dropdown_element)
    
    # Select by visible text
    select.select_by_visible_text("Option 1")
    assert select.first_selected_option.text == "Option 1"
    
    # Select by value
    select.select_by_value("2")
    assert select.first_selected_option.text == "Option 2"
    
    # Select by index
    select.select_by_index(1)
    assert select.first_selected_option.text == "Option 1"
    
    # Get all options
    all_options = select.options
    assert len(all_options) == 3  # Including "Please select an option"


# ============================================================================
# JAVASCRIPT EXECUTION
# ============================================================================

def test_javascript_execution(driver):
    """Demonstrates executing JavaScript in the browser"""
    driver.get("https://www.selenium.dev")
    
    # Execute JavaScript to scroll
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    # Get page title using JavaScript
    title = driver.execute_script("return document.title;")
    assert len(title) > 0
    
    # Highlight an element using JavaScript
    element = driver.find_element(By.TAG_NAME, "h1")
    driver.execute_script(
        "arguments[0].style.border='3px solid red'", 
        element
    )
    
    # Get element properties
    inner_html = driver.execute_script(
        "return arguments[0].innerHTML;", 
        element
    )
    assert len(inner_html) > 0
    
    # Create and trigger custom event
    driver.execute_script("""
        var event = new CustomEvent('testEvent', { detail: 'test data' });
        document.dispatchEvent(event);
    """)


def test_scroll_to_element(driver):
    """Demonstrates scrolling to a specific element"""
    driver.get("https://www.selenium.dev/documentation/")
    
    # Find an element further down the page
    footer = driver.find_element(By.TAG_NAME, "footer")
    
    # Scroll element into view
    driver.execute_script("arguments[0].scrollIntoView(true);", footer)
    time.sleep(1)
    
    # Verify element is in viewport
    is_in_viewport = driver.execute_script("""
        var elem = arguments[0];
        var rect = elem.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)
        );
    """, footer)
    
    assert is_in_viewport


# ============================================================================
# SCREENSHOT AND EVIDENCE CAPTURE
# ============================================================================

def test_screenshot_capture(driver):
    """Demonstrates taking screenshots"""
    driver.get("https://www.selenium.dev")
    
    # Create screenshots directory if it doesn't exist
    screenshot_dir = "test_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Full page screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"{screenshot_dir}/full_page_{timestamp}.png"
    driver.save_screenshot(screenshot_path)
    assert os.path.exists(screenshot_path)
    
    # Element screenshot
    element = driver.find_element(By.TAG_NAME, "h1")
    element_screenshot_path = f"{screenshot_dir}/element_{timestamp}.png"
    element.screenshot(element_screenshot_path)
    assert os.path.exists(element_screenshot_path)


def test_screenshot_on_failure(driver):
    """Demonstrates capturing screenshot on test failure"""
    screenshot_dir = "test_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    try:
        driver.get("https://www.selenium.dev")
        # Intentionally fail to demonstrate screenshot capture
        assert False, "Intentional failure for demo"
    except AssertionError:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"{screenshot_dir}/failure_{timestamp}.png")
        raise


# ============================================================================
# COOKIE MANAGEMENT
# ============================================================================

def test_cookie_management(driver):
    """Demonstrates cookie handling"""
    driver.get("https://www.selenium.dev")
    
    # Add a cookie
    driver.add_cookie({
        "name": "test_cookie",
        "value": "test_value",
        "path": "/",
        "secure": False
    })
    
    # Get specific cookie
    test_cookie = driver.get_cookie("test_cookie")
    assert test_cookie["value"] == "test_value"
    
    # Get all cookies
    all_cookies = driver.get_cookies()
    assert len(all_cookies) > 0
    
    # Delete specific cookie
    driver.delete_cookie("test_cookie")
    assert driver.get_cookie("test_cookie") is None
    
    # Delete all cookies
    driver.delete_all_cookies()
    assert len(driver.get_cookies()) == 0


# ============================================================================
# CUSTOM EXPECTED CONDITIONS
# ============================================================================

class element_has_css_class:
    """Custom expected condition: element has specific CSS class"""
    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class
        
    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        classes = element.get_attribute("class")
        if classes and self.css_class in classes:
            return element
        return False


class text_to_be_present_in_element_attribute:
    """Custom expected condition: text present in element attribute"""
    def __init__(self, locator, attribute, text):
        self.locator = locator
        self.attribute = attribute
        self.text = text
        
    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        attribute_value = element.get_attribute(self.attribute)
        if attribute_value and self.text in attribute_value:
            return True
        return False


def test_custom_expected_conditions(driver):
    """Demonstrates using custom expected conditions"""
    driver.get("https://www.selenium.dev")
    
    # Wait for element to have specific class (if applicable)
    # This is a demonstration of the pattern
    try:
        element = WebDriverWait(driver, 10).until(
            element_has_css_class((By.TAG_NAME, "body"), "site")
        )
        print(f"Found element with class: {element.get_attribute('class')}")
    except TimeoutException:
        print("Element didn't get the expected class within timeout")


# ============================================================================
# DYNAMIC CONTENT AND AJAX
# ============================================================================

def test_wait_for_ajax(driver):
    """Demonstrates waiting for AJAX/dynamic content"""
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Click start button
    start_button = driver.find_element(By.CSS_SELECTOR, "#start button")
    start_button.click()
    
    # Wait for loading indicator to disappear
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loading"))
    )
    
    # Wait for finish text to appear
    finish_text = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "finish"))
    )
    
    assert "Hello World!" in finish_text.text


def test_wait_for_element_attribute_change(driver):
    """Demonstrates waiting for element attribute changes"""
    driver.get("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Find the checkbox
    checkbox = driver.find_element(By.CSS_SELECTOR, "#checkbox input")
    remove_button = driver.find_element(By.CSS_SELECTOR, "#checkbox-example button")
    
    # Remove checkbox
    remove_button.click()
    
    # Wait for checkbox to be gone
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#checkbox input"))
    )
    
    # Verify message appears
    message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "message"))
    )
    assert "gone" in message.text.lower()


# ============================================================================
# STALE ELEMENT HANDLING
# ============================================================================

def test_handle_stale_element(driver):
    """Demonstrates handling stale element reference"""
    driver.get("https://the-internet.herokuapp.com/dynamic_controls")
    
    enable_button = driver.find_element(By.CSS_SELECTOR, "#input-example button")
    input_field = driver.find_element(By.CSS_SELECTOR, "#input-example input")
    
    # Click enable
    enable_button.click()
    
    # Wait for input to be enabled
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#input-example input"))
    )
    
    # Re-find the element to avoid stale reference
    input_field = driver.find_element(By.CSS_SELECTOR, "#input-example input")
    input_field.send_keys("Test input")
    
    assert input_field.get_attribute("value") == "Test input"


# ============================================================================
# FILE UPLOAD
# ============================================================================

def test_file_upload(driver):
    """Demonstrates file upload"""
    driver.get("https://the-internet.herokuapp.com/upload")
    
    # Create a temporary test file
    test_file_path = os.path.abspath("test_upload.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file for upload")
    
    try:
        # Find file input and send file path
        file_input = driver.find_element(By.ID, "file-upload")
        file_input.send_keys(test_file_path)
        
        # Submit
        submit_button = driver.find_element(By.ID, "file-submit")
        submit_button.click()
        
        # Wait for upload confirmation
        uploaded_file = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uploaded-files"))
        )
        
        assert "test_upload.txt" in uploaded_file.text
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


# ============================================================================
# BROWSER NAVIGATION
# ============================================================================

def test_browser_navigation(driver):
    """Demonstrates browser navigation methods"""
    # Navigate to first page
    driver.get("https://www.selenium.dev")
    first_url = driver.current_url
    
    # Navigate to second page
    driver.get("https://www.selenium.dev/documentation/")
    second_url = driver.current_url
    
    assert first_url != second_url
    
    # Go back
    driver.back()
    assert driver.current_url == first_url
    
    # Go forward
    driver.forward()
    assert driver.current_url == second_url
    
    # Refresh
    driver.refresh()
    assert driver.current_url == second_url


# ============================================================================
# ELEMENT STATE CHECKS
# ============================================================================

def test_element_state_verification(driver):
    """Demonstrates checking various element states"""
    driver.get("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Check if element is displayed
    checkbox = driver.find_element(By.CSS_SELECTOR, "#checkbox input")
    assert checkbox.is_displayed()
    
    # Check if element is enabled
    input_field = driver.find_element(By.CSS_SELECTOR, "#input-example input")
    is_enabled_initially = input_field.is_enabled()
    
    # Click enable button
    enable_button = driver.find_element(By.CSS_SELECTOR, "#input-example button")
    enable_button.click()
    
    # Wait and check if state changed
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#input-example input"))
    )
    
    input_field = driver.find_element(By.CSS_SELECTOR, "#input-example input")
    assert input_field.is_enabled() != is_enabled_initially
    
    # Check if checkbox is selected
    checkbox = driver.find_element(By.CSS_SELECTOR, "#checkbox input")
    initial_state = checkbox.is_selected()
    checkbox.click()
    assert checkbox.is_selected() != initial_state


# ============================================================================
# TABLE HANDLING
# ============================================================================

def test_table_data_extraction(driver):
    """Demonstrates extracting data from HTML tables"""
    driver.get("https://the-internet.herokuapp.com/tables")
    
    # Get all rows from table 1
    rows = driver.find_elements(By.CSS_SELECTOR, "#table1 tbody tr")
    
    # Extract data from first row
    first_row_cells = rows[0].find_elements(By.TAG_NAME, "td")
    first_row_data = [cell.text for cell in first_row_cells]
    
    assert len(first_row_data) > 0
    
    # Find specific data in table
    last_names = driver.find_elements(By.CSS_SELECTOR, "#table1 tbody tr td:nth-child(1)")
    last_name_texts = [name.text for name in last_names]
    
    assert len(last_name_texts) > 0
    
    # Click on sortable column header
    header = driver.find_element(By.CSS_SELECTOR, "#table1 thead tr th.header:nth-child(1)")
    header.click()
    time.sleep(1)
    
    # Get data after sort
    sorted_last_names = driver.find_elements(By.CSS_SELECTOR, "#table1 tbody tr td:nth-child(1)")
    sorted_texts = [name.text for name in sorted_last_names]
    
    # Verify order changed (in some way)
    print(f"Original order: {last_name_texts}")
    print(f"Sorted order: {sorted_texts}")


# ============================================================================
# DATA-DRIVEN TESTING
# ============================================================================

test_data = [
    ("https://www.selenium.dev", "Selenium"),
    ("https://www.python.org", "Python"),
    ("https://www.github.com", "GitHub"),
]

@pytest.mark.parametrize("url,expected_text", test_data)
def test_data_driven(driver, url, expected_text):
    """Demonstrates data-driven testing"""
    driver.get(url)
    page_source = driver.page_source.lower()
    assert expected_text.lower() in page_source


# ============================================================================
# PERFORMANCE AND TIMING
# ============================================================================

def test_page_load_performance(driver):
    """Demonstrates measuring page load performance"""
    start_time = time.time()
    driver.get("https://www.selenium.dev")
    end_time = time.time()
    
    load_time = end_time - start_time
    print(f"Page load time: {load_time:.2f} seconds")
    
    # Use Navigation Timing API
    navigation_start = driver.execute_script("return window.performance.timing.navigationStart")
    response_start = driver.execute_script("return window.performance.timing.responseStart")
    dom_complete = driver.execute_script("return window.performance.timing.domComplete")
    
    backend_time = (response_start - navigation_start) / 1000
    frontend_time = (dom_complete - response_start) / 1000
    
    print(f"Backend time: {backend_time:.2f}s")
    print(f"Frontend time: {frontend_time:.2f}s")
    
    # Assert reasonable load time (adjust threshold as needed)
    assert load_time < 30, f"Page took too long to load: {load_time}s"


# ============================================================================
# FLAKY TEST HANDLING WITH RETRY
# ============================================================================

@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_with_retry(driver):
    """Demonstrates retry mechanism for flaky tests (requires pytest-rerunfailures)"""
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    start_button = driver.find_element(By.CSS_SELECTOR, "#start button")
    start_button.click()
    
    # This might be flaky due to timing issues
    finish_text = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "finish"))
    )
    
    assert "Hello World!" in finish_text.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
