# Senior Automation Engineer Quiz
## Design Patterns & Framework Architecture

---

### Section 1: Pattern Identification (20 points)

**Q1.** You have 83 test files with hardcoded URLs. When the staging URL changes, you need to update all 83 files. Which pattern solves this, and what's the key technical principle?

<details>
<summary>Answer</summary>

**Pattern:** Singleton Pattern (Config class)

**Technical Principle:** Single source of truth - one instance holds configuration, accessible globally without creating multiple copies.

**Implementation:** `__new__` method ensures only one instance exists, even with multiple calls.
</details>

---

**Q2.** Your BasePage has this code:
```python
def find_element(self, locator):
    if wait_type == "clickable":
        return WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(locator))
    elif wait_type == "visible":
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
    elif wait_type == "presence":
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
```
What pattern should replace this? Why is the current approach a code smell?

<details>
<summary>Answer</summary>

**Pattern:** Strategy Pattern

**Why it's a code smell:**
- Violates Open/Closed Principle (must modify method to add new wait types)
- Hard to test individual wait strategies
- Mixing algorithm selection with algorithm implementation
- Will grow into unmaintainable if/elif chain

**Better approach:**
```python
class WaitStrategy(ABC):
    @abstractmethod
    def wait(self, driver, locator): pass

class ClickableWait(WaitStrategy):
    def wait(self, driver, locator):
        return WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))

# Usage: find_element(locator, ClickableWait())
```
</details>

---

**Q3.** You need to add screenshot capture to 50 test methods when they fail. You don't want to modify the test code itself. What pattern and why?

<details>
<summary>Answer</summary>

**Pattern:** Decorator Pattern

**Why:**
- Non-invasive: adds behavior without modifying original function
- Composable: can stack multiple decorators (@log @screenshot @retry)
- Separation of concerns: cross-cutting concerns separate from test logic
- Pythonic: uses native `@decorator` syntax

**Example:**
```python
@screenshot_on_failure
def test_something(driver):
    # test logic - no try/catch needed
```
</details>

---

### Section 2: Code Review (30 points)

**Q4.** Review this code. Identify at least 3 issues and suggest improvements:

```python
class LoginPage(driver):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login")
    
    def login(self, user, pwd, driver)-> 'loginPage' :
        self.type(self.USERNAME_input,user)
        
        self.type(self.PASSWORD_INPUT, pwd)
        self.click(self.LOGIN_BUTTON, ClickableWait())
        return self
```

<details>
<summary>Answer</summary>

**Issues:**

1. **Invalid inheritance:** `class LoginPage(driver):` - can't inherit from driver instance, should inherit from BasePage
2. **No driver stored:** No `__init__` method to store driver reference, so `self.type()` and `self.click()` have no driver to work with
3. **No waits:** Without BasePage inheritance and proper driver, there's no wait mechanism before interactions
4. **Inconsistent locator names:** Uses `USERNAME` but calls `self.USERNAME_input` (typo), `LOGIN_BTN` defined but uses `LOGIN_BUTTON`
5. **Driver passed as parameter:** `login(self, user, pwd, driver)` - driver should be stored in `__init__`, not passed to every method
6. **Inconsistent return type hint:** `-> 'loginPage'` should be `-> 'LoginPage'` (capitalization)

**Improved version:**
```python
class LoginPage(BasePage):
    # Locators as class constants
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login")
    
    def __init__(self, driver: webdriver.Remote):
        super().__init__(driver)  # BasePage stores driver and sets up waits
    
    def login(self, user: str, pwd: str) -> 'LoginPage':
        # self.type() and self.click() inherited from BasePage
        # They include built-in wait strategies
        self.type(self.USERNAME_INPUT, user)  # BasePage.type() waits for visibility
        self.type(self.PASSWORD_INPUT, pwd)
        self.click(self.LOGIN_BUTTON, ClickableWait())  # Explicit clickable wait
        return self  # Fluent interface
```

**Why this is better:**
- BasePage `__init__` stores `self.driver` and sets up `WebDriverWait`
- `self.type()` and `self.click()` from BasePage have wait strategies built-in
- Proper inheritance chain: LoginPage → BasePage → driver methods
- No need to pass driver to every method (stored once in `__init__`)
</details>

---

**Q5.** This Element wrapper has a bug. What is it and how do you fix it?

```python
class Element:
    def __init__(self, driver, locator):
        self.driver = driver
        self.locator = locator
        self.element = driver.find_element(*locator)
    
    def click(self):
        self.element.click()
    
    def type(self, text):
        self.element.send_keys(text)
```

<details>
<summary>Answer</summary>

**Bug:** Element is found once in `__init__` and cached. If the page changes or element is re-rendered, you'll get `StaleElementReferenceException`.

**Fix:** Use a property to re-find element on each access:

```python
class Element:
    def __init__(self, driver, locator):
        self.driver = driver
        self.locator = locator
        self._element = None  # Don't store element
    
    @property
    def webelement(self) -> WebElement:
        """Get fresh WebElement to avoid stale references"""
        self._element = self.driver.find_element(*self.locator)
        return self._element
    
    def click(self):
        self.webelement.click()  # Always fresh
    
    def type(self, text):
        self.webelement.send_keys(text)
```
</details>

---

### Section 3: Architecture Decisions (30 points)

**Q6.** Your team has 3 environments (dev, staging, prod) with different URLs, timeouts, and browser settings. How do you design the configuration system? Include:
- Pattern choice and why
- How to switch between environments
- Where config values are stored
- How tests access config

<details>
<summary>Answer</summary>

**Pattern:** Singleton + Factory (Config loading)

**Design:**

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.load_from_environment()
    
    def load_from_environment(self):
        env = os.getenv('TEST_ENV', 'dev')
        config_file = f'config/{env}.json'
        with open(config_file) as f:
            data = json.load(f)
            self.base_url = data['base_url']
            self.timeout = data['timeout']
            self.browser = data['browser']
```

**Storage:** JSON/YAML files per environment (config/dev.json, config/staging.json)

**Environment switching:** `export TEST_ENV=staging` or pytest.ini

**Test access:** `config = Config()` (always same instance)

**Why:**
- Single source of truth
- Environment-specific without code changes
- Easy to add new environments
- No hardcoded values in tests
</details>

---

**Q7.** You need to support Chrome, Firefox, and Edge with different options for each. Some tests need headless, some don't. Design the driver creation system.

<details>
<summary>Answer</summary>

**Pattern:** Factory Pattern + Strategy (for options)

**Design:**

```python
from abc import ABC, abstractmethod
from enum import Enum
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Strategy Pattern - Different browser configuration strategies
class BrowserStrategy(ABC):
    """Abstract strategy for browser configuration"""
    
    @abstractmethod
    def configure_options(self, headless: bool):
        """Configure browser-specific options"""
        pass
    
    @abstractmethod
    def create_driver(self, options):
        """Create driver with configured options"""
        pass

class ChromeStrategy(BrowserStrategy):
    def configure_options(self, headless: bool):
        opts = ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        if headless:
            opts.add_argument("--headless=new")
        return opts
    
    def create_driver(self, options):
        return webdriver.Chrome(options=options)

class FirefoxStrategy(BrowserStrategy):
    def configure_options(self, headless: bool):
        opts = FirefoxOptions()
        opts.add_argument("--width=1920")
        opts.add_argument("--height=1080")
        if headless:
            opts.add_argument("--headless")
        return opts
    
    def create_driver(self, options):
        return webdriver.Firefox(options=options)

class EdgeStrategy(BrowserStrategy):
    def configure_options(self, headless: bool):
        opts = EdgeOptions()
        opts.add_argument("--no-sandbox")
        if headless:
            opts.add_argument("--headless")
        return opts
    
    def create_driver(self, options):
        return webdriver.Edge(options=options)

# Factory Pattern - Creates appropriate strategy and driver
class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"

class DriverFactory:
    """Factory for creating WebDriver instances using strategy pattern"""
    
    # Map browser types to their strategies
    _strategies = {
        BrowserType.CHROME: ChromeStrategy(),
        BrowserType.FIREFOX: FirefoxStrategy(),
        BrowserType.EDGE: EdgeStrategy()
    }
    
    @staticmethod
    def create_driver(browser_type: BrowserType, headless: bool = False):
        """
        Create driver using appropriate strategy
        
        Args:
            browser_type: Type of browser to create
            headless: Whether to run in headless mode
        
        Returns:
            Configured WebDriver instance
        """
        strategy = DriverFactory._strategies.get(browser_type)
        if not strategy:
            raise ValueError(f"Unsupported browser: {browser_type}")
        
        # Strategy pattern in action: delegate to browser-specific strategy
        options = strategy.configure_options(headless)
        driver = strategy.create_driver(options)
        
        # Common configuration for all browsers
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver
```

**Pytest fixture:**
```python
@pytest.fixture
def driver(request):
    """
    Fixture that creates driver based on command-line options
    Usage: pytest --browser=firefox --headless
    """
    browser = request.config.getoption("--browser", default="chrome")
    headless = request.config.getoption("--headless", default=False)
    
    driver = DriverFactory.create_driver(
        BrowserType[browser.upper()], 
        headless=headless
    )
    
    yield driver
    driver.quit()

# conftest.py - Add command-line options
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true", default=False)
```

**Why Factory + Strategy:**
- **Factory:** Centralizes driver creation, maps browser types to strategies
- **Strategy:** Each browser has its own configuration logic (Chrome needs --no-sandbox, Firefox doesn't)
- Easy to add new browsers: create new strategy class, add to `_strategies` dict
- Easy to extend: add custom options per browser without affecting others
- Swappable: Change browser behavior at runtime without modifying tests
- Test doesn't care about driver creation details
- Command-line control: `pytest --browser=firefox --headless`

**Senior insight:** The Strategy pattern is crucial here because each browser requires different options and initialization. Without it, you'd have nested if/else blocks with browser-specific logic scattered throughout the factory.
</details>

---

**Q8.** Explain when you would use each wait approach and why:

a) `driver.implicitly_wait(10)`  
b) `WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))`  
c) `time.sleep(5)`  
d) Custom wait condition with polling

<details>
<summary>Answer</summary>

**a) Implicit Wait:**
- **When:** Global fallback for simple scripts
- **Why:** Applied to all find_element calls automatically
- **Downside:** Can't change timeout per element, not recommended for frameworks

**b) Explicit Wait (WebDriverWait):**
- **When:** Production framework (ALWAYS use this)
- **Why:** Specific timeout per action, intelligent polling, fails fast when condition met
- **Example:** Waiting for element to be clickable before clicking

**c) time.sleep():**
- **When:** ALMOST NEVER in production code
- **Only acceptable use:** Debugging/troubleshooting temporarily
- **Why bad:** Wastes time (always waits full duration), not dynamic, not intelligent

**d) Custom Wait Condition:**
- **When:** Built-in conditions don't cover your case
- **Example:** Wait for element count to equal 5, wait for CSS property value, wait for AJAX complete
- **Why:** Reusable, testable, same interface as built-in conditions

**Senior insight:** Explicit waits are non-negotiable for production. Implicit waits + explicit waits together can cause unexpected timeouts (they stack).
</details>

---

### Section 4: Practical Scenarios (20 points)

**Q9.** Your tests have StaleElementReferenceException in 30% of CI runs. Explain:
- Why this happens
- 3 different solutions (with tradeoffs)
- Which solution you'd choose and why

<details>
<summary>Answer</summary>

**Why it happens:**
DOM updates/re-renders after you've cached the WebElement reference. Element pointer becomes invalid.

**Solutions:**

1. **Re-find element each time (no caching)**
   - Pro: Simple, always fresh
   - Con: Slower (extra find operations)
   - Implementation: Don't store elements, always `find_element()` when needed

2. **Element Wrapper with @property**
   - Pro: Transparent, clean API, always fresh
   - Con: Slight overhead
   - Implementation: Element class with `@property webelement` that re-finds

3. **Retry decorator on methods**
   - Pro: Handles stale + other transient errors
   - Con: Retries might hide real issues, slower on failures
   - Implementation: `@retry_on_stale(max_attempts=3)`

4. **Wait for staleness then re-find**
   - Pro: Explicit handling when you know re-render happens
   - Con: Requires knowing when to apply it
   - Implementation: `WebDriverWait(driver, 10).until(EC.staleness_of(element))`

**Best choice:** **Element Wrapper (#2)**
- Clean abstraction, always works
- No changes to test code
- Handles problem at framework level
- Small performance cost is worth reliability

**Senior insight:** If you're seeing 30% failure rate, it's a framework problem, not a test problem. Fix it at the framework level once, not in 100 tests.
</details>

---

**Q10.** Design a retry mechanism that:
- Retries on TimeoutException and StaleElementReferenceException only
- Does NOT retry on AssertionError
- Logs each attempt
- Has configurable max attempts and delay
- Can be applied via decorator

<details>
<summary>Answer</summary>

```python
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

def retry_on_exceptions(
    exceptions: Tuple[Type[Exception], ...] = (TimeoutException, StaleElementReferenceException),
    max_attempts: int = 3,
    delay: int = 1
):
    """
    Decorator to retry test on specific exceptions
    
    Args:
        exceptions: Tuple of exception types to retry on
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_attempts}: {func.__name__}")
                    result = func(*args, **kwargs)
                    logger.info(f"Success on attempt {attempt}: {func.__name__}")
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt} failed with {type(e).__name__}: {str(e)}"
                    )
                    if attempt < max_attempts:
                        logger.info(f"Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
                
                except Exception as e:
                    # Don't retry on other exceptions (like AssertionError)
                    logger.error(f"Non-retryable exception: {type(e).__name__}")
                    raise
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

# Usage:
@retry_on_exceptions(
    exceptions=(TimeoutException, StaleElementReferenceException),
    max_attempts=3,
    delay=2
)
def test_flaky_element(driver):
    # Test that might have stale elements or timeouts
    element = driver.find_element(By.ID, "dynamic")
    element.click()
    assert "success" in driver.current_url  # This won't be retried if it fails
```

**Key points:**
- Uses `exceptions` tuple to catch specific errors
- Other exceptions (AssertionError) propagate immediately (no retry)
- Configurable via decorator parameters
- Proper logging for debugging
- Preserves original function metadata with `@wraps`
</details>

---

## Scoring Guide

- **18-20 points:** Senior level - Ready for senior automation roles
- **15-17 points:** Mid-Senior level - Solid understanding, minor gaps
- **12-14 points:** Mid level - Good foundation, needs more pattern practice
- **Below 12:** Junior-Mid level - Focus on framework design patterns

---

## Bonus Question (10 extra points)

**Q11.** Your framework has these issues:
1. Tests are slow (2 minutes each)
2. Flaky (20% failure rate in CI)
3. Hard to maintain (locator changes require many file updates)
4. New team members struggle to write tests

Design a complete framework refactor plan addressing all issues. Include:
- Patterns to apply
- Architecture decisions
- Migration strategy
- Success metrics

<details>
<summary>Answer</summary>

**Framework Refactor Plan:**

### Issue 1: Speed (2 min per test)
**Root causes:**
- Excessive implicit waits
- No page load optimization
- Sequential execution

**Solutions:**
- Replace implicit waits with explicit waits (fail fast)
- Implement parallel execution (pytest-xdist)
- Add browser caching for suite setup
- Profile tests to find bottlenecks
```python
# pytest.ini
[pytest]
addopts = -n auto --timeout=30
```

### Issue 2: Flaky (20% failure)
**Root causes:**
- Stale elements
- Race conditions
- Poor wait strategies

**Solutions:**
- Element Wrapper pattern (auto re-find)
- Strategy pattern for waits (right wait for each action)
- Retry decorator for transient failures
- Better assertions (wait for condition, not just assert)
```python
# Before: assert element.is_displayed()
# After: WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))
```

### Issue 3: Hard to maintain
**Root causes:**
- Locators scattered in tests
- Duplication
- No abstraction

**Solutions:**
- Page Object Model (locators in page classes)
- Base Page with common methods
- Fluent interface for readability
```python
class LoginPage(BasePage):
    USERNAME = (By.ID, "user")
    PASSWORD = (By.ID, "pass")
    
    def login(self, user, pwd):
        return self.type(self.USERNAME, user).type(self.PASSWORD, pwd).click(self.LOGIN_BTN)
```

### Issue 4: New team members struggle
**Root causes:**
- No documentation
- Complex WebDriver code visible
- Inconsistent patterns

**Solutions:**
- Fluent interface (tests read like English)
- Hide WebDriver complexity in BasePage
- Examples and templates
- Enforce patterns with code reviews
```python
# Easy for new team members:
LoginPage(driver).login("user", "pass").verify_logged_in()
```

### Architecture

```
framework/
├── core/
│   ├── base_page.py (BasePage with common methods)
│   ├── config.py (Singleton config)
│   ├── driver_factory.py (Factory for drivers)
│   └── wait_strategies.py (Strategy pattern waits)
├── pages/
│   ├── login_page.py
│   ├── dashboard_page.py
│   └── ...
├── tests/
│   └── test_*.py (only test logic, no WebDriver)
├── utils/
│   ├── decorators.py (@retry, @screenshot)
│   └── custom_conditions.py
└── config/
    ├── dev.json
    └── staging.json
```

### Migration Strategy

**Phase 1: Foundation (Week 1)**
- Implement BasePage, Config, DriverFactory
- Create 2-3 page objects as examples
- Document patterns and provide templates

**Phase 2: Convert Core Flows (Week 2-3)**
- Convert login, main navigation flows
- Run old tests in parallel with new (compare results)
- Train team on new patterns

**Phase 3: Parallel Development (Week 4-8)**
- New tests use new framework (mandatory)
- Convert old tests incrementally
- Delete old framework code as tests migrate

**Phase 4: Optimization (Ongoing)**
- Profile and optimize slow tests
- Tune waits and parallelization
- Gather metrics

### Success Metrics

| Metric | Before | Target | Timeline |
|--------|--------|--------|----------|
| Test execution time | 2 min | 30 sec | 4 weeks |
| Flaky rate | 20% | <2% | 6 weeks |
| Lines to change locator | 50+ | 1 | Immediate |
| Onboarding time | 2 weeks | 3 days | 8 weeks |
| Code coverage | Unknown | >80% | 12 weeks |

### Patterns Applied
- ✅ Singleton (Config)
- ✅ Factory (Driver creation)
- ✅ Strategy (Wait strategies)
- ✅ Page Object (Maintainability)
- ✅ Fluent Interface (Readability)
- ✅ Decorator (Cross-cutting concerns)
- ✅ Wrapper (Stale element handling)

**Key Insight:** Framework problems require framework solutions. Don't fix symptoms in tests - fix root causes in framework architecture.
</details>

---

## Study Recommendations

Based on your score:

### If you scored well on Section 1 but struggled with Section 2:
Focus on code reviews and real-world codebases. Theory is good, but you need to spot anti-patterns in real code.

### If you scored well on Sections 1-2 but struggled with Section 3:
Practice architectural design. Try designing frameworks from scratch for different scenarios.

### If you struggled with Section 4:
You need more hands-on debugging experience. The scenarios in Section 4 are based on real production issues.

### Next Steps:
1. Implement each pattern from scratch in a personal project
2. Review open-source test frameworks (pytest-selenium, robotframework)
3. Practice explaining patterns without looking at notes
4. Do code reviews focusing on identifying patterns and anti-patterns
