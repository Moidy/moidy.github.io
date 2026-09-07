"""
Advanced Selenium Framework Patterns

This file demonstrates advanced framework design patterns commonly discussed in senior-level interviews:
- Base Page class with reusable methods
- Fluent interface pattern
- Factory pattern for driver creation
- Decorator pattern for test execution
- Strategy pattern for waits
- Custom exceptions
- Logging and reporting
- Configuration management

================================================================================
QUICK REFERENCE - MEMORIZATION AID
================================================================================

THE "3 AM TEST" - Will you hate yourself if this breaks at 3 AM?

PATTERN          | 3 AM NIGHTMARE                        | TECHNICAL WIN
-----------------|---------------------------------------|----------------------------------
SINGLETON        | Changing URL in 50 files             | Single source of truth
(Config)         |                                      | Memory efficient
                 |                                      |
FACTORY          | Adding Chrome option to 40 tests     | Encapsulated creation
(DriverFactory)  |                                      | Easy to extend
                 |                                      |
STRATEGY         | Adding new wait type = editing       | Swappable algorithms
(WaitStrategy)   | 30 methods                           | Open/Closed principle
                 |                                      |
PAGE OBJECT      | Button ID changed, 83 files to       | DRY - change once
(BasePage)       | update                               | Test readability
                 |                                      |
FLUENT           | Tests look like random function      | Natural language flow
(method chain)   | calls                                | Less verbose
                 |                                      |
DECORATOR        | Forgot screenshot in 40% of tests    | Non-invasive enhancement
(@screenshot)    |                                      | Composable behavior
                 |                                      |
WRAPPER          | StaleElementException everywhere     | Fresh references
(Element)        |                                      | Enhanced API

MEMORY TRICK: "I'm annoyed by X, so I use Y"
- Annoyed by scattered config → Singleton
- Annoyed by setup duplication → Factory  
- Annoyed by if/else wait types → Strategy
- Annoyed by duplicate locators → Page Object
- Annoyed by ugly test code → Fluent Interface
- Annoyed by try/catch everywhere → Decorator
- Annoyed by stale elements → Wrapper

================================================================================
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Tuple, List, Optional, Callable
import pytest
import logging
import functools
from abc import ABC, abstractmethod
from enum import Enum
import json


# ============================================================================
# CUSTOM EXCEPTIONS - DOMAIN-SPECIFIC ERROR HANDLING
# ============================================================================
# ANNOYING PROBLEM:
#   - Generic "Exception" doesn't tell you WHAT went wrong WHERE
#   - Selenium's exceptions too broad (TimeoutException for everything)
#   - Can't catch specific framework issues vs Selenium issues
#   - Hard to provide helpful error messages for your specific app
#
# TECHNICAL BENEFITS:
#   - Clarity: Exception name tells you exactly what failed
#   - Specific Handling: catch ElementNotInteractableError vs generic Exception
#   - Better Debugging: Stack traces show YOUR exception names
#   - Documentation: Exception class itself documents failure scenarios
#   - Error Hierarchy: Can create exception inheritance tree
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Test fails with "Exception" - which of 20 possible issues was it?
#   - Want to retry on specific errors but not others
#   - Need to provide business-friendly error messages
# ============================================================================

class ElementNotInteractableError(Exception):
    """Custom exception for non-interactable elements"""
    pass


class PageNotLoadedError(Exception):
    """Custom exception for page load failures"""
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Page failed to load"
        super().__init__(message)


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION MANAGEMENT - SINGLETON PATTERN
# ============================================================================
# ANNOYING PROBLEM:
#   - Base URL, timeouts, and settings copy-pasted in 50+ test files
#   - Need to change base URL? Update 50 files manually
#   - Each test creates its own config → inconsistent settings
#   - Hard to maintain: dev/staging/prod configs scattered everywhere
#
# TECHNICAL BENEFITS:
#   - Single source of truth: ONE place to change config values
#   - Memory efficient: Only one Config instance exists in memory
#   - Thread-safe when properly implemented with locks
#   - Lazy initialization: Config created only when first accessed
#   - Easy environment switching: Load from file once, use everywhere
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Updating hardcoded URLs in 83 test files at 3 AM
#   - Half your tests use timeout=10, half use timeout=15 (inconsistent)
#   - QA says "use staging URL" and you want to cry
# ============================================================================

class Config:
    """Configuration management using singleton pattern"""
    _instance = None
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.base_url = "https://www.selenium.dev"
        self.implicit_wait = 10
        self.explicit_wait = 10
        self.page_load_timeout = 30
        self.browser = "chrome"
        self.headless = False
        self._initialized = True
    
    @classmethod
    def from_file(cls, config_file: str):
        """Load configuration from JSON file"""
        instance = cls()
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
        return instance


# ============================================================================
# FACTORY PATTERN - DRIVER CREATION
# ============================================================================
# ANNOYING PROBLEM:
#   - Same 15 lines of Chrome setup duplicated in every test file
#   - Boss says "add Firefox support" → copy-paste nightmare begins
#   - Different developers set up drivers differently (inconsistent)
#   - Want to add logging/monitoring to all drivers? Good luck
#
# TECHNICAL BENEFITS:
#   - Encapsulation: Complex driver setup hidden in one place
#   - Easy to extend: Add new browser by adding one method
#   - Consistent driver configuration across all tests
#   - Single Responsibility: Driver creation separated from test logic
#   - Open/Closed Principle: Open for extension (new browsers), closed for modification
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Need to add one Chrome option → editing 40 test files
#   - Different environments need different driver configs
#   - Trying to debug why some tests have headless and others don't
# ============================================================================

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


class DriverFactory:
    """Factory pattern for creating WebDriver instances"""
    
    @staticmethod
    def create_driver(browser_type: BrowserType = BrowserType.CHROME, 
                     headless: bool = False) -> webdriver.Remote:
        """Create and configure a WebDriver instance"""
        logger.info(f"Creating {browser_type.value} driver (headless={headless})")
        
        if browser_type == BrowserType.CHROME:
            return DriverFactory._create_chrome_driver(headless)
        elif browser_type == BrowserType.FIREFOX:
            return DriverFactory._create_firefox_driver(headless)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
    
    @staticmethod
    def _create_chrome_driver(headless: bool) -> webdriver.Chrome:
        """Create Chrome driver with options"""
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        
        if headless:
            opts.add_argument("--headless=new")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        
        config = Config()
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.set_script_timeout(config.implicit_wait)
        
        return driver
    
    @staticmethod
    def _create_firefox_driver(headless: bool) -> webdriver.Firefox:
        """Create Firefox driver with options"""
        # Placeholder for Firefox implementation
        raise NotImplementedError("Firefox driver not yet implemented")


# ============================================================================
# STRATEGY PATTERN - WAIT CONDITIONS
# ============================================================================
# ANNOYING PROBLEM:
#   - Some elements need visibility wait, some need clickable wait
#   - Your BasePage.find_element() has ugly if/else blocks for wait types
#   - Adding new wait type means editing every method that uses waits
#   - Can't easily swap wait behavior at runtime
#
# TECHNICAL BENEFITS:
#   - Polymorphism: Different strategies with same interface
#   - Swappable behavior: Change wait type without changing calling code
#   - Easy to test: Mock different strategies independently
#   - Adheres to Open/Closed: Add new wait types without modifying existing code
#   - Composition over inheritance: Inject strategy instead of subclassing
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Need "wait for custom attribute" → rewriting find_element() logic
#   - Some tests need patient waits, others need quick fails
#   - if wait_type == 'clickable': elif wait_type == 'visible': elif... (code smell)
# ============================================================================

class WaitStrategy(ABC):
    """Abstract base class for wait strategies"""
    
    @abstractmethod
    def wait(self, driver: webdriver.Remote, locator: Tuple[str, str]) -> WebElement:
        """Wait for element with specific strategy"""
        pass


class PresenceWait(WaitStrategy):
    """Wait for element presence in DOM"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def wait(self, driver: webdriver.Remote, locator: Tuple[str, str]) -> WebElement:
        logger.debug(f"Waiting for presence: {locator}")
        return WebDriverWait(driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )


class VisibilityWait(WaitStrategy):
    """Wait for element to be visible"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def wait(self, driver: webdriver.Remote, locator: Tuple[str, str]) -> WebElement:
        logger.debug(f"Waiting for visibility: {locator}")
        return WebDriverWait(driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )


class ClickableWait(WaitStrategy):
    """Wait for element to be clickable"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def wait(self, driver: webdriver.Remote, locator: Tuple[str, str]) -> WebElement:
        logger.debug(f"Waiting for clickable: {locator}")
        return WebDriverWait(driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )


class InvisibilityWait(WaitStrategy):
    """Wait for element to be invisible"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def wait(self, driver: webdriver.Remote, locator: Tuple[str, str]) -> bool:
        logger.debug(f"Waiting for invisibility: {locator}")
        return WebDriverWait(driver, self.timeout).until(
            EC.invisibility_of_element_located(locator)
        )


# ============================================================================
# PAGE OBJECT MODEL (POM) - BASE PAGE
# ============================================================================
# ANNOYING PROBLEM:
#   - Locators scattered in 100+ test files
#   - Dev changes button ID → updating 83 test files
#   - Same helper methods (click, type, wait) duplicated everywhere
#   - Test code full of ugly WebDriver calls, hard to read
#
# TECHNICAL BENEFITS:
#   - DRY: Reusable methods defined once, used everywhere
#   - Maintainability: Change locator once, all tests updated
#   - Readability: Tests read like business actions, not WebDriver calls
#   - Separation of Concerns: Test logic vs page interactions separated
#   - Inheritance: Specific pages inherit common functionality
#
# WHEN YOU'LL FEEL THE PAIN:
#   - "Login button" ID changed → finding all 67 references manually
#   - Every test has driver.find_element(By.ID, "...").click() → repetitive
#   - New QA can't understand tests because they're full of WebDriver code
# ============================================================================

class BasePage:
    """Base page class with reusable methods - foundation of Page Object Model"""
    
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.config = Config()
        self.wait = WebDriverWait(driver, self.config.explicit_wait)
    
    def open(self, url: str):
        """Navigate to URL"""
        logger.info(f"Opening URL: {url}")
        self.driver.get(url)
        return self
    
    def find_element(self, locator: Tuple[str, str], 
                    wait_strategy: WaitStrategy = None) -> WebElement:
        """Find element with optional wait strategy"""
        if wait_strategy:
            return wait_strategy.wait(self.driver, locator)
        return self.driver.find_element(*locator)
    
    def find_elements(self, locator: Tuple[str, str]) -> List[WebElement]:
        """Find multiple elements"""
        logger.debug(f"Finding elements: {locator}")
        return self.driver.find_elements(*locator)
    
    def click(self, locator: Tuple[str, str], wait_strategy: WaitStrategy = None):
        """Click element with optional wait"""
        logger.info(f"Clicking element: {locator}")
        element = self.find_element(locator, wait_strategy or ClickableWait())
        
        try:
            element.click()
        except Exception as e:
            logger.error(f"Failed to click element: {e}")
            # Try JavaScript click as fallback
            self.driver.execute_script("arguments[0].click();", element)
        
        return self
    
    def type(self, locator: Tuple[str, str], text: str, 
            clear_first: bool = True) -> 'BasePage':
        """Type text into element"""
        logger.info(f"Typing '{text}' into element: {locator}")
        element = self.find_element(locator, VisibilityWait())
        
        if clear_first:
            element.clear()
        
        element.send_keys(text)
        return self
    
    def get_text(self, locator: Tuple[str, str]) -> str:
        """Get text from element"""
        logger.debug(f"Getting text from element: {locator}")
        element = self.find_element(locator, PresenceWait())
        return element.text
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str) -> str:
        """Get attribute value from element"""
        logger.debug(f"Getting attribute '{attribute}' from element: {locator}")
        element = self.find_element(locator, PresenceWait())
        return element.get_attribute(attribute)
    
    def is_displayed(self, locator: Tuple[str, str]) -> bool:
        """Check if element is displayed"""
        try:
            element = self.find_element(locator, PresenceWait())
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False
    
    def is_enabled(self, locator: Tuple[str, str]) -> bool:
        """Check if element is enabled"""
        element = self.find_element(locator, PresenceWait())
        return element.is_enabled()
    
    def wait_for_url_contains(self, text: str, timeout: int = 10) -> bool:
        """Wait for URL to contain specific text"""
        logger.debug(f"Waiting for URL to contain: {text}")
        return WebDriverWait(self.driver, timeout).until(
            EC.url_contains(text)
        )
    
    def wait_for_title_contains(self, text: str, timeout: int = 10) -> bool:
        """Wait for page title to contain specific text"""
        logger.debug(f"Waiting for title to contain: {text}")
        return WebDriverWait(self.driver, timeout).until(
            EC.title_contains(text)
        )
    
    def scroll_to_element(self, locator: Tuple[str, str]):
        """Scroll element into view"""
        logger.debug(f"Scrolling to element: {locator}")
        element = self.find_element(locator, PresenceWait())
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return self
    
    def execute_script(self, script: str, *args):
        """Execute JavaScript"""
        logger.debug(f"Executing script: {script[:50]}...")
        return self.driver.execute_script(script, *args)
    
    def take_screenshot(self, filename: str):
        """Take screenshot"""
        logger.info(f"Taking screenshot: {filename}")
        self.driver.save_screenshot(filename)
        return self
    
    @property
    def current_url(self) -> str:
        """Get current URL"""
        return self.driver.current_url
    
    @property
    def title(self) -> str:
        """Get page title"""
        return self.driver.title


# ============================================================================
# FLUENT INTERFACE PATTERN - METHOD CHAINING
# ============================================================================
# ANNOYING PROBLEM:
#   - Test code looks like disconnected function calls
#   - page.navigate() then page.search() then page.verify() → ugly
#   - Hard to follow the flow of actions in a test
#   - Lots of temporary variables cluttering test code
#
# TECHNICAL BENEFITS:
#   - Readability: Code reads like natural language sentences
#   - Less verbose: Fewer variable declarations needed
#   - Method chaining: return self from each method
#   - Natural flow: Actions read in sequence like a story
#   - Builder-like pattern: Construct complex operations fluently
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Test looks like random function calls instead of user journey
#   - Code reviews: "What's the sequence of actions here?"
#   - Want elegant test code: page.login().search("item").verify()
# ============================================================================

class SearchPage(BasePage):
    """Example page object with fluent interface"""
    
    # Locators
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.NAME, "btnK")
    RESULTS_STATS = (By.ID, "result-stats")
    
    def __init__(self, driver: webdriver.Remote):
        super().__init__(driver)
        self.url = "https://www.google.com"
    
    def navigate(self) -> 'SearchPage':
        """Navigate to search page"""
        self.open(self.url)
        return self
    
    def search_for(self, query: str) -> 'SearchPage':
        """Perform search - demonstrates fluent interface"""
        self.type(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        return self
    
    def get_results_text(self) -> str:
        """Get results text"""
        return self.get_text(self.RESULTS_STATS)
    
    def verify_results_present(self) -> 'SearchPage':
        """Verify search results are present"""
        assert self.is_displayed(self.RESULTS_STATS), "Search results not displayed"
        return self


# ============================================================================
# DECORATOR PATTERN - TEST ENHANCEMENT
# ============================================================================
# ANNOYING PROBLEM:
#   - Every test needs try/except/screenshot boilerplate
#   - Forgot to add screenshot code in 40% of tests
#   - Want logging on all tests → editing 100+ test functions
#   - Retry logic copy-pasted everywhere with slight variations
#
# TECHNICAL BENEFITS:
#   - Separation of Concerns: Core test logic separate from cross-cutting concerns
#   - Reusability: Write @screenshot_on_failure once, use everywhere
#   - Non-invasive: Add behavior without modifying original test code
#   - Composable: Stack multiple decorators (@log @screenshot @retry)
#   - Pythonic: Uses native Python decorator syntax
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Test fails in CI, no screenshot, can't debug what happened
#   - Adding retry to 50 tests means editing all 50 functions
#   - Same try/catch/logging boilerplate in every single test
# ============================================================================

def screenshot_on_failure(func):
    """Decorator to capture screenshot on test failure"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Find driver instance in args
            driver = None
            for arg in args:
                if isinstance(arg, webdriver.Remote):
                    driver = arg
                    break
                elif hasattr(arg, 'driver') and isinstance(arg.driver, webdriver.Remote):
                    driver = arg.driver
                    break
            
            if driver:
                timestamp = pytest.timestamp if hasattr(pytest, 'timestamp') else 'error'
                screenshot_name = f"failure_{func.__name__}_{timestamp}.png"
                driver.save_screenshot(screenshot_name)
                logger.error(f"Test failed, screenshot saved: {screenshot_name}")
            
            raise e
    return wrapper


def log_test_execution(func):
    """Decorator to log test execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting test: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Test passed: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Test failed: {func.__name__} - {str(e)}")
            raise
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: int = 1):
    """Decorator to retry test on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Attempt {attempt + 1}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


# ============================================================================
# CUSTOM EXPECTED CONDITIONS - EXTENSION PATTERN
# ============================================================================
# ANNOYING PROBLEM:
#   - Selenium's built-in conditions don't cover your specific needs
#   - Waiting for "CSS property to equal X" requires ugly custom code
#   - Same complex wait logic duplicated in multiple tests
#   - Hard to test/reuse complex wait conditions
#
# TECHNICAL BENEFITS:
#   - Reusability: Complex wait logic defined once, used everywhere
#   - Consistency: Same interface as Selenium's built-in conditions
#   - Testable: Each condition can be unit tested independently
#   - Extensible: Easy to add new custom conditions as needed
#   - Clean Tests: Hide complexity behind descriptive method names
#
# WHEN YOU'LL FEEL THE PAIN:
#   - Waiting for "element count to be 5" → ugly lambda in every test
#   - Need to wait for AJAX complete in 20 different places
#   - Custom conditions logic duplicated with slight variations
# ============================================================================

class CustomConditions:
    """Custom expected conditions for complex scenarios"""
    
    @staticmethod
    def element_attribute_contains(locator: Tuple[str, str], 
                                   attribute: str, 
                                   value: str) -> Callable:
        """Wait for element attribute to contain value"""
        def condition(driver):
            try:
                element = driver.find_element(*locator)
                attr_value = element.get_attribute(attribute)
                return attr_value and value in attr_value
            except:
                return False
        return condition
    
    @staticmethod
    def element_count_to_be(locator: Tuple[str, str], count: int) -> Callable:
        """Wait for specific number of elements"""
        def condition(driver):
            elements = driver.find_elements(*locator)
            return len(elements) == count
        return condition
    
    @staticmethod
    def url_matches_regex(pattern: str) -> Callable:
        """Wait for URL to match regex pattern"""
        import re
        def condition(driver):
            return re.search(pattern, driver.current_url) is not None
        return condition
    
    @staticmethod
    def element_has_css_value(locator: Tuple[str, str], 
                             property_name: str, 
                             value: str) -> Callable:
        """Wait for element to have specific CSS value"""
        def condition(driver):
            try:
                element = driver.find_element(*locator)
                css_value = element.value_of_css_property(property_name)
                return css_value == value
            except:
                return False
        return condition
    
    @staticmethod
    def ajax_complete() -> Callable:
        """Wait for jQuery AJAX calls to complete"""
        def condition(driver):
            try:
                return driver.execute_script("return jQuery.active == 0")
            except:
                return True  # If jQuery not present, assume no AJAX
        return condition


# ============================================================================
# WRAPPER PATTERN - ELEMENT WRAPPER
# ============================================================================
# ANNOYING PROBLEM:
#   - StaleElementReferenceException everywhere (element cached, page changed)
#   - Every click needs try/except/JavaScript fallback boilerplate
#   - Adding behavior to WebElement requires subclassing (can't do it)
#   - Same element.clear() then element.send_keys() pattern everywhere
#
# TECHNICAL BENEFITS:
#   - Encapsulation: Wrap WebElement with additional behavior
#   - Stale Reference Solution: Re-find element on each access (fresh reference)
#   - Enhanced API: Add helper methods (type, wait_until_visible, etc.)
#   - Error Handling: Centralized handling for common issues (stale, not clickable)
#   - Lazy Evaluation: Element found only when accessed (avoids timing issues)
#
# WHEN YOU'LL FEEL THE PAIN:
#   - StaleElementReferenceException in 30% of test runs
#   - Every click has try/except with JavaScript fallback
#   - Want to add retry logic to all element interactions
# ============================================================================

class Element:
    """Wrapper class for WebElement with additional functionality"""
    
    def __init__(self, driver: webdriver.Remote, locator: Tuple[str, str]):
        self.driver = driver
        self.locator = locator
        self._element = None
    
    @property
    def webelement(self) -> WebElement:
        """Get fresh WebElement to avoid stale references"""
        self._element = self.driver.find_element(*self.locator)
        return self._element
    
    def click(self, force: bool = False):
        """Click with retry and fallback to JavaScript"""
        try:
            self.webelement.click()
        except Exception as e:
            if force:
                logger.warning(f"Normal click failed, using JavaScript: {e}")
                self.driver.execute_script("arguments[0].click();", self.webelement)
            else:
                raise
        return self
    
    def type(self, text: str, clear: bool = True):
        """Type text with optional clear"""
        element = self.webelement
        if clear:
            element.clear()
        element.send_keys(text)
        return self
    
    def is_visible(self) -> bool:
        """Check if element is visible"""
        try:
            return self.webelement.is_displayed()
        except:
            return False
    
    def wait_until_visible(self, timeout: int = 10):
        """Wait until element is visible"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.locator)
        )
        return self
    
    def wait_until_clickable(self, timeout: int = 10):
        """Wait until element is clickable"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.locator)
        )
        return self
    
    @property
    def text(self) -> str:
        """Get element text"""
        return self.webelement.text
    
    def get_attribute(self, name: str) -> str:
        """Get element attribute"""
        return self.webelement.get_attribute(name)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def config():
    """Configuration fixture"""
    return Config()


@pytest.fixture
def driver(config):
    """Driver fixture using factory pattern"""
    driver = DriverFactory.create_driver(
        BrowserType.CHROME,
        headless=config.headless
    )
    yield driver
    logger.info("Closing driver")
    driver.quit()


# ============================================================================
# EXAMPLE TESTS USING FRAMEWORK
# ============================================================================

@log_test_execution
@screenshot_on_failure
def test_fluent_interface_pattern(driver):
    """Demonstrates fluent interface pattern"""
    search_page = SearchPage(driver)
    
    # Chain methods using fluent interface
    (search_page
     .navigate()
     .search_for("Selenium WebDriver")
     .verify_results_present())
    
    results_text = search_page.get_results_text()
    assert len(results_text) > 0


def test_custom_wait_conditions(driver):
    """Demonstrates custom wait conditions"""
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    # Click start
    start_button = driver.find_element(By.CSS_SELECTOR, "#start button")
    start_button.click()
    
    # Use custom condition for element count
    WebDriverWait(driver, 10).until(
        CustomConditions.element_count_to_be((By.ID, "loading"), 1)
    )
    
    # Wait for loading to disappear
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loading"))
    )
    
    # Verify finish message
    finish = driver.find_element(By.ID, "finish")
    assert "Hello World!" in finish.text


def test_strategy_pattern_waits(driver):
    """Demonstrates wait strategy pattern"""
    base_page = BasePage(driver)
    base_page.open("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Use different wait strategies
    checkbox_locator = (By.CSS_SELECTOR, "#checkbox input")
    
    # Wait for presence
    base_page.find_element(checkbox_locator, PresenceWait(timeout=10))
    
    # Wait for visibility
    base_page.find_element(checkbox_locator, VisibilityWait(timeout=10))
    
    # Click using clickable wait
    base_page.click(checkbox_locator, ClickableWait(timeout=10))


@retry_on_failure(max_attempts=3, delay=2)
def test_with_retry_decorator(driver):
    """Demonstrates retry decorator"""
    driver.get("https://the-internet.herokuapp.com/dynamic_loading/2")
    
    start_button = driver.find_element(By.CSS_SELECTOR, "#start button")
    start_button.click()
    
    # This might be flaky, but retry will help
    finish_text = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "finish"))
    )
    
    assert "Hello World!" in finish_text.text


def test_element_wrapper_class(driver):
    """Demonstrates element wrapper pattern"""
    driver.get("https://the-internet.herokuapp.com/dynamic_controls")
    
    # Create wrapped element
    input_element = Element(driver, (By.CSS_SELECTOR, "#input-example input"))
    enable_button = Element(driver, (By.CSS_SELECTOR, "#input-example button"))
    
    # Use wrapper methods
    enable_button.wait_until_clickable().click()
    
    # Wait and type
    input_element.wait_until_visible().type("Test text")
    
    assert input_element.get_attribute("value") == "Test text"


def test_base_page_chaining(driver):
    """Demonstrates method chaining with base page"""
    page = BasePage(driver)
    
    # Chain operations
    (page
     .open("https://the-internet.herokuapp.com/login")
     .type((By.ID, "username"), "tomsmith")
     .type((By.ID, "password"), "SuperSecretPassword!")
     .click((By.CSS_SELECTOR, "button[type='submit']")))
    
    # Verify login success
    success_message = page.get_text((By.CSS_SELECTOR, ".flash.success"))
    assert "logged into" in success_message.lower()


def test_driver_factory_pattern(config):
    """Demonstrates driver factory pattern"""
    # Create driver using factory
    driver1 = DriverFactory.create_driver(BrowserType.CHROME, headless=False)
    
    try:
        driver1.get("https://www.selenium.dev")
        assert "Selenium" in driver1.title
    finally:
        driver1.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
