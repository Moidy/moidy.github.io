# Advanced Selenium Test Examples - Interview Preparation Guide

This repository contains comprehensive Selenium WebDriver examples covering advanced topics commonly asked in interviews.

## Files Overview

### 1. `test_advanced_selenium.py`
Contains practical examples of advanced Selenium techniques:
- Page Object Model (POM)
- Multiple windows/tabs handling
- iFrame interactions
- Alert/popup handling (accept, dismiss, send keys)
- Drag and drop operations
- Hover and mouse actions
- Select/dropdown handling
- JavaScript execution
- Screenshot capture
- Cookie management
- Custom expected conditions
- Dynamic content/AJAX waiting
- Stale element handling
- File upload
- Browser navigation
- Element state verification
- Table data extraction
- Data-driven testing with parametrization
- Performance measurement

### 2. `test_framework_patterns.py`
Demonstrates framework design patterns and best practices:
- Base Page Object class with reusable methods
- Fluent interface pattern (method chaining)
- Factory pattern for driver creation
- Strategy pattern for different wait types
- Decorator pattern for test enhancement
- Custom wait conditions
- Element wrapper class
- Singleton configuration management
- Custom exceptions
- Logging and reporting
- Retry mechanisms

## Key Interview Topics Covered

### 1. **Waits and Synchronization**
```python
# Implicit Wait
driver.implicitly_wait(10)

# Explicit Wait
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element"))
)

# Custom Wait Conditions
WebDriverWait(driver, 10).until(
    CustomConditions.element_count_to_be((By.CLASS, "item"), 5)
)
```

**Interview Questions:**
- What's the difference between implicit and explicit waits?
        - implicit is a general wait without a loop to check for a condition that would exit upon being true
        - Explicit wait is then there is a na element, object or condition of the site that would indicate it is clear to carry on with the next step in test
- When should you use each type of wait?
        - implicit waits should be rarely used over explicit waits, useful in simple situations but at scale in a suite can cause long waiting
        - Explicit should be used where possible, can be used for exactness
- How do you handle dynamic/AJAX content?
        - Dynamic content can be tricky, if on an infinate scrolling platform its can be difficult to know where to stop
        - One startegy is to forgo CSS for ids and xpaths exactl;y but matching content for testing can be difficult if the load order is unknown and the tags random like on reddit

### 2. **Page Object Model (POM)**
```python
class LoginPage(BasePage):
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    def login(self, username, password):
        self.type(self.USERNAME_FIELD, username)
        self.type(self.PASSWORD_FIELD, password)
        self.click(self.LOGIN_BUTTON)
        return HomePage(self.driver)
```

**Interview Questions:**
- What is Page Object Model and why use it?
    - The Page object model is a design pattern for enhancing test maintenance and reducing code duplication
        There is a clean separation between the test code and page-specific code, such as locators (or their use if you’re using a UI Map) and layout.
        single point of change
- How does POM improve test maintenance?
    - seperates the locator logic from the the tezt code
- What are the benefits of separating page logic from test logic?
    - should a change be needed to the page l;ayout but not the functionality it is a change in one place over many

### 3. **Handling Different Element States**
```python
# Check visibility
element.is_displayed()

# Check if enabled
element.is_enabled()

# Check if selected (checkboxes/radio buttons)
element.is_selected()

# Wait for element to be clickable
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "button"))
)
```

**Interview Questions:**
- How do you verify an element is ready for interaction?
    - I would use the findbyelemnt method or I would use manual tools on the Browser
- What's the difference between presence and visibility?
    - presence mean that it may be in the DOM but nor rendered yet. Visibility means it has been rendered to the UI
- How do you handle elements that appear after AJAX calls?
   - explicit waits on driver.execute_script
- Constant dom inspection and dynamic element locators
        Use relative locators: Prefer stable attributes such as name, class, or data-* attributes over volatile ones like id.

### 4. **Multiple Windows/Tabs**
```python
# Store original window
original_window = driver.current_window_handle

# Open new window
driver.execute_script("window.open('url', '_blank');")

# Switch to new window
for handle in driver.window_handles:
    if handle != original_window:
        driver.switch_to.window(handle)

# Close and switch back
driver.close()
driver.switch_to.window(original_window)
```

**Interview Questions:**
- How do you handle multiple browser windows?
        - using the selenium driver.current_window_handle you can track current windows
        you can save the handle as current and use similar vars to store other states for easy switch between
        like so : original_window_handle = driver.current_window_handle

        to create a new window you can select the element to create a new tab using : 
        driver.find_element(By.LINK_TEXT, "Open new window").click()
        wait.until(EC.number_of_windows_to_be(2))

        store it within a new var for easy reuse:
        new_window_handle = (set(driver.window_handles) - {original_window_handle}).pop()

        swapping between windows can be achieved with: 
        driver.switch_to.window(new_window_handle)


- What's the difference between window handles and tabs?
        there is none, sleenmium treats all tabs and windows as window handles
- How do you switch between windows?
    by using the window handle Id
    driver.switch_to.window(new_window_handle)

### 5. **iFrame Handling**
```python
# Switch to iframe by element
iframe = driver.find_element(By.ID, "iframe-id")
driver.switch_to.frame(iframe)

# Switch to iframe by index
driver.switch_to.frame(0)

# Switch back to default content
driver.switch_to.default_content()
```

**Interview Questions:**
- How do you interact with elements inside an iframe?
    - Switch to the iframe first, then you should be able to navigate the elements inside and locate them
- What happens if you don't switch to iframe context?
    - The driver will remain in the main document context and will NOT be able to see or interact with elements inside the iframe. You must explicitly switch into the iframe to access its contents.
- How do you handle nested iframes?
    - You must switch to them **in order from parent to child** - you cannot skip levels. Switch to the outer iframe first, then from that context, switch to the inner iframe.
    ```python
    # Switch to outer iframe
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@id='outer']"))
    )
    # Now switch to inner iframe (nested inside the outer one)
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@id='inner']"))
    )
    # Now you can interact with elements in the inner iframe
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "button-in-nested-iframe"))
    )
    # To go back to main content, use:
    driver.switch_to.default_content()
    ```

### 6. **JavaScript Execution**
```python
# Scroll to element
driver.execute_script("arguments[0].scrollIntoView(true);", element)

# Click using JavaScript
driver.execute_script("arguments[0].click();", element)

# Get return value
title = driver.execute_script("return document.title;")

# Modify DOM
driver.execute_script(
    "arguments[0].style.border='3px solid red'", 
    element
)
```

**Interview Questions:**
- When would you use JavaScript execution over Selenium methods?
    - **When Selenium's click() fails**: Element is obscured by another element, has an overlay, or is not in the viewport
    - **Scrolling**: JavaScript scrolling (`scrollIntoView()`) is more reliable than ActionChains
    - **Hidden elements**: Selenium can't interact with `display:none` or `visibility:hidden` elements, but JavaScript can
    - **Reading properties**: Access computed CSS values, inner dimensions, scroll positions that aren't directly available via Selenium
    - **Performance**: Bulk operations (like extracting data from many elements) can be faster with one JavaScript call
    - **DOM manipulation**: Modifying attributes, injecting HTML, or triggering events directly
    - **Checking page state**: Verify `document.readyState`, check if `jQuery.active == 0` for AJAX completion
    - **Shadow DOM**: Access elements inside shadow DOM trees
    - Example scenarios:
        ```python
        # Click when element is blocked
        driver.execute_script("arguments[0].click();", element)
        
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        # Set value on disabled input
        driver.execute_script("arguments[0].value = 'test';", disabled_input)
        ```
- How do you execute JavaScript that returns a value?
    - Use the `return` keyword in your JavaScript and assign the result to a variable:
        ```python
        title = driver.execute_script("return document.title;")
        page_height = driver.execute_script("return document.body.scrollHeight;")
        is_visible = driver.execute_script(
            "return arguments[0].offsetParent !== null;", element
        )
        ```
- What are common use cases for JavaScript execution?
    - Scrolling (to top, bottom, specific element)
    - Clicking elements that Selenium can't click
    - Highlighting elements for debugging/screenshots
    - Checking if page is fully loaded
    - Extracting data that's not directly accessible
    - Working with custom web components or Shadow DOM

### 7. **Action Chains**
```python
from selenium.webdriver.common.action_chains import ActionChains

# Hover over element
ActionChains(driver).move_to_element(element).perform()

# Drag and drop
ActionChains(driver).drag_and_drop(source, target).perform()

# Complex chain
actions = ActionChains(driver)
actions.move_to_element(menu)
actions.click(submenu)
actions.perform()
```

**Interview Questions:**
- How do you perform complex user interactions?
    - using action chains to queue actions to be performed 
- What's the difference between click() and ActionChains click?
    - Actions.click is simpler and will just send a click event to the obkect
     - element.click tends to have conditions on the object and will check its valid before it can interact with the object
- How do you simulate keyboard shortcuts?
    - actions chain keydown the command key and .sendkeys the others

### 8. **Design Patterns**

**Factory Pattern:**
```python
class DriverFactory:
    @staticmethod
    def create_driver(browser_type):
        if browser_type == "chrome":
            return webdriver.Chrome()
        elif browser_type == "firefox":
            return webdriver.Firefox()
```

**Strategy Pattern:**
```python
class WaitStrategy(ABC):
    @abstractmethod
    def wait(self, driver, locator):
        pass

class VisibilityWait(WaitStrategy):
    def wait(self, driver, locator):
        return WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(locator)
        )
```

**Interview Questions:**
- What design patterns are useful in test automation?
    - patterns lead to more maintainable codebases and reduce duplication of non test code
    Page Object Model (POM) - encapsulates page elements and actions
    Factory Pattern - creates different browser drivers
    Strategy Pattern - different wait strategies
    Singleton Pattern - single configuration instance
    Builder Pattern - complex object construction
    Decorator Pattern - add functionality (logging, screenshots on failure)
- How does Factory pattern help in cross-browser testing?
    - allows a single point for new browser configurations to be inserted and accessed with identical configuration
- Why use Strategy pattern for waits?
    - keeps waits uniform in usage when interacting with elements withing the test suite across users

### 9. **Exception Handling**
```python
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "element"))
    )
except TimeoutException:
    logger.error("Element not found within timeout")
    driver.save_screenshot("timeout_error.png")
except StaleElementReferenceException:
    # Re-find the element
    element = driver.find_element(By.ID, "element")
```

**Interview Questions:**
- What are common Selenium exceptions?
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
- How do you handle StaleElementReferenceException?
    Wait for the element to be com interactable
    refresh the init of the POM object
    try catch method
- When should you catch exceptions vs. let them fail?
    - Catch when you can recover (StaleElement → re-find), when testing expected failures, or to add debugging info. 
    Let fail when it indicates a genuine bug, failed assertion, or there's no recovery strategy. 
    Don't use try/catch to compensate for missing waits - fix timing issues with proper explicit waits instead

### 10. **Test Data Management**
```python
# Parametrized tests
@pytest.mark.parametrize("username,password,expected", [
    ("user1", "pass1", True),
    ("user2", "pass2", False),
    ("admin", "admin123", True),
])
def test_login(driver, username, password, expected):
    login_page = LoginPage(driver)
    result = login_page.login(username, password)
    assert result == expected
```

**Interview Questions:**
- How do you implement data-driven testing?
        in python you use paramaterisation
        you could also build data classes with onjects and use those objects
- What are different ways to manage test data?
        csv files
        json
        database
        fictures
        envvars
        test data builders
- How do you handle test data for multiple environments?
        configuration filers per environment
        env vars
        CMD args
        seperate test data files
        credentials

## Running the Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

The `requirements.txt` should include:
```
selenium
webdriver-manager
pytest
pytest-rerunfailures
```

### Run all tests
```bash
pytest tests/ -v -s
```

### Run specific test file
```bash
pytest tests/test_advanced_selenium.py -v
```

### Run specific test
```bash
pytest tests/test_advanced_selenium.py::test_page_object_model -v
```

### Run tests in parallel (requires pytest-xdist)
```bash
pytest tests/ -n 4 -v
```

### Generate HTML report (requires pytest-html)
```bash
pytest tests/ --html=report.html --self-contained-html
```

## Interview Preparation Tips

### 1. **Common Interview Questions**

**Q: What is Selenium WebDriver?**
A: Selenium WebDriver is a web automation framework that allows you to control browsers programmatically. It provides language-specific bindings to control browsers and supports multiple browsers (Chrome, Firefox, Edge, Safari).

**Q: Explain the architecture of Selenium WebDriver.**
A: Selenium WebDriver has three main components:
- **Client Libraries**: Language bindings (Python, Java, C#, etc.)
- **JSON Wire Protocol/W3C WebDriver Protocol**: Communication protocol between client and browser
- **Browser Drivers**: Executables that control specific browsers (ChromeDriver, GeckoDriver, etc.)

**Q: What are locator strategies in Selenium?**
A: Selenium provides 8 locator strategies:
- ID: `By.ID`
- Name: `By.NAME`
- Class Name: `By.CLASS_NAME`
- Tag Name: `By.TAG_NAME`
- Link Text: `By.LINK_TEXT`
- Partial Link Text: `By.PARTIAL_LINK_TEXT`
- CSS Selector: `By.CSS_SELECTOR`
- XPath: `By.XPATH`

**Q: CSS Selector vs XPath - which is better?**
A: 
- **CSS Selectors**: Faster, more readable, but can only traverse forward
- **XPath**: More powerful, can traverse backwards, but slower
- **Recommendation**: Use CSS for simple cases, XPath when you need parent/sibling navigation

**Q: How do you handle dynamic elements?**
A:
1. Use explicit waits with expected conditions
2. Use custom wait conditions
3. Re-find elements to avoid stale references
4. Use dynamic locators (partial matches, contains)

**Q: What is StaleElementReferenceException?**
A: Occurs when an element is no longer attached to the DOM. Solutions:
- Re-find the element
- Use try-except and retry logic
- Use element wrapper that finds element fresh each time

**Q: How do you verify an element is present vs visible?**
A:
- **Presence**: Element exists in DOM (might not be visible)
- **Visibility**: Element is visible and has height/width > 0
- Use `presence_of_element_located` vs `visibility_of_element_located`

**Q: How would you implement a test automation framework?**
A:
1. Choose test framework (pytest, unittest)
2. Implement Page Object Model
3. Add configuration management
4. Implement driver factory for multiple browsers
5. Add logging and reporting
6. Implement data-driven testing
7. Add CI/CD integration
8. Implement parallel execution

**Q: How do you handle flaky tests?**
A:
1. Identify root cause (timing issues, test dependencies)
2. Add appropriate waits
3. Implement retry mechanism
4. Isolate tests (no dependencies between tests)
5. Use stable locators
6. Ensure proper test data setup/teardown

**Q: What's the difference between findElement and findElements?**
A:
- `findElement`: Returns first matching element, throws exception if not found
- `findElements`: Returns list of all matching elements, returns empty list if none found

**Q: How do you take screenshots in Selenium?**
A:
```python
# Full page
driver.save_screenshot("screenshot.png")

# Specific element
element.screenshot("element.png")

# As bytes
screenshot_bytes = driver.get_screenshot_as_png()
```

### 2. **Coding Exercise Preparation**

Practice implementing these during interview:

1. **Login Test with POM**
   - Create LoginPage class
   - Implement login method
   - Verify successful/failed login

2. **Dynamic Wait Implementation**
   - Wait for element to appear
   - Wait for element to have specific text
   - Wait for element count to be N

3. **Data Extraction from Table**
   - Extract all data from table
   - Find specific row
   - Sort and verify

4. **File Upload Test**
   - Upload file
   - Verify upload success
   - Handle different file types

5. **Multi-Window Scenario**
   - Open link in new tab
   - Perform action in new tab
   - Switch back and verify

### 3. **Best Practices to Mention**

1. **Use explicit waits over implicit waits**
2. **Implement Page Object Model**
3. **Use meaningful locators (avoid indexes)**
4. **Don't use Thread.sleep() - use proper waits**
5. **Implement proper exception handling**
6. **Take screenshots on failures**
7. **Keep tests independent and isolated**
8. **Use configuration files for environment-specific data**
9. **Implement logging for debugging**
10. **Follow naming conventions**

### 4. **Framework Design Discussion**

Be prepared to discuss:
- Test structure and organization
- Configuration management
- Test data management
- Reporting and logging
- CI/CD integration
- Parallel execution
- Cross-browser testing
- Page Object Model variations

### 5. **Advanced Topics**

If interviewing for senior positions:
- Selenium Grid for distributed testing
- Docker for test environments
- Headless browser testing
- Visual regression testing
- Performance testing integration
- BDD with Cucumber/Behave
- Test reporting frameworks
- Custom test frameworks

## Common Pitfalls to Avoid

1. ❌ Using `Thread.sleep()` instead of explicit waits
2. ❌ Not handling StaleElementReferenceException
3. ❌ Hard-coding test data in tests
4. ❌ Not taking screenshots on failures
5. ❌ Creating element references once and reusing
6. ❌ Not switching back from iframe/window context
7. ❌ Using indexes in locators (brittle)
8. ❌ Not closing browser after tests
9. ❌ Having test dependencies (tests affect each other)
10. ❌ Not logging important actions

## Additional Resources

- **Selenium Documentation**: https://www.selenium.dev/documentation/
- **Selenium Python Docs**: https://selenium-python.readthedocs.io/
- **WebDriver W3C Spec**: https://www.w3.org/TR/webdriver/
- **Test Automation University**: https://testautomationu.applitools.com/

## Practice Websites

These examples use several practice websites:
- https://the-internet.herokuapp.com/ (Various test scenarios)
- https://www.selenium.dev (Real Selenium site)
- https://jqueryui.com (Interactive elements)

## Tips for Interview Day

1. **Talk through your approach** before coding
2. **Ask clarifying questions** about requirements
3. **Start with simple solution**, then improve
4. **Explain trade-offs** of different approaches
5. **Handle edge cases** and exceptions
6. **Write clean, readable code** with comments
7. **Test your code** if possible
8. **Be honest** if you don't know something

## Questions to Ask Interviewer

- What test automation framework do you currently use?
- How is your testing integrated with CI/CD?
- What's your approach to handling flaky tests?
- How do you manage test data?
- What browsers and platforms do you support?
- How do you handle mobile testing?
- What's your ratio of unit/integration/e2e tests?

Good luck with your interview! 🚀
