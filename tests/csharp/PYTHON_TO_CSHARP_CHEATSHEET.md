# Python to C# Cheat Sheet - Selenium Framework Patterns

## Side-by-Side Pattern Comparison

### 1. SINGLETON PATTERN

#### Python
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
        self.base_url = "https://example.com"
        self._initialized = True

# Usage
config = Config()
```

#### C#
```csharp
public sealed class Config
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    public string BaseUrl { get; set; }
    
    private Config()
    {
        BaseUrl = "https://example.com";
    }
}

// Usage
var config = Config.Instance;
```

**Key difference:** C# uses `Lazy<T>` for thread-safe lazy init. Much cleaner!

---

### 2. FACTORY PATTERN

#### Python
```python
class DriverFactory:
    @staticmethod
    def create_driver(browser_type, headless=False):
        if browser_type == BrowserType.CHROME:
            return DriverFactory._create_chrome(headless)
        elif browser_type == BrowserType.FIREFOX:
            return DriverFactory._create_firefox(headless)
    
    @staticmethod
    def _create_chrome(headless):
        opts = Options()
        opts.add_argument("--no-sandbox")
        if headless:
            opts.add_argument("--headless=new")
        return webdriver.Chrome(options=opts)
```

#### C#
```csharp
public static class DriverFactory 
{
    public static IWebDriver CreateDriver(BrowserType browserType, bool headless = false)
    {
        if (browserType == BrowserType.Chrome)
            return CreateChrome(headless);
        else if (browserType == BrowserType.Firefox)
            return CreateFirefox(headless);
        
        throw new ArgumentException($"Unsupported: {browserType}");
    }
    
    private static IWebDriver CreateChrome(bool headless)
    {
        var opts = new ChromeOptions();
        opts.AddArgument("--no-sandbox");
        if (headless)
            opts.AddArgument("--headless=new");
        return new ChromeDriver(opts);
    }
}
```

**Key difference:** 
- Python: `@staticmethod` → C#: `static` keyword in method signature
- Python: `webdriver.Chrome()` → C#: `new ChromeDriver()`

---

### 3. STRATEGY PATTERN

#### Python
```python
from abc import ABC, abstractmethod

class WaitStrategy(ABC):
    @abstractmethod
    def wait(self, driver, locator):
        pass

class ClickableWait(WaitStrategy):
    def wait(self, driver, locator):
        return WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(locator)
        )

# Usage
strategy = ClickableWait()
element = strategy.wait(driver, (By.ID, "btn"))
```

#### C#
```csharp
public interface IWaitStrategy
{
    IWebElement Wait(IWebDriver driver, By locator, int timeout = 10);
}

public class ClickableWait : IWaitStrategy
{
    public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
    {
        var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
        return wait.Until(ExpectedConditions.ElementToBeClickable(locator));
    }
}

// Usage
var strategy = new ClickableWait();
var element = strategy.Wait(driver, By.Id("btn"));
```

**Key difference:**
- Python: ABC → C#: `interface`
- Python: `(By.ID, "btn")` → C#: `By.Id("btn")`
- Python: No `new` keyword → C#: `new ClickableWait()`

---

### 4. PAGE OBJECT MODEL

#### Python
```python
class BasePage:
    def __init__(self, driver):
        self.driver = driver
    
    def click(self, locator):
        element = self.driver.find_element(*locator)
        element.click()
        return self

class LoginPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def login(self, user, pwd):
        self.type(self.USERNAME, user)
        self.type(self.PASSWORD, pwd)
        return self
```

#### C#
```csharp
public class BasePage
{
    protected IWebDriver Driver;
    
    public BasePage(IWebDriver driver)
    {
        Driver = driver;
    }
    
    public BasePage Click(By locator)
    {
        var element = Driver.FindElement(locator);
        element.Click();
        return this;
    }
}

public class LoginPage : BasePage
{
    private static readonly By Username = By.Id("username");
    private static readonly By Password = By.Id("password");
    
    public LoginPage(IWebDriver driver) : base(driver)
    {
    }
    
    public LoginPage Login(string user, string pwd)
    {
        Type(Username, user);
        Type(Password, pwd);
        return this;
    }
}
```

**Key differences:**
- Python: `self` → C#: `this`
- Python: `def __init__` → C#: Constructor with class name
- Python: `super().__init__(driver)` → C#: `: base(driver)`
- Python: `return self` → C#: `return this;`
- Python: Capital variable → C#: `private static readonly`

---

### 5. FLUENT INTERFACE

#### Python
```python
class LoginPage(BasePage):
    def enter_username(self, username):
        self.type(self.USERNAME, username)
        return self  # Enable chaining
    
    def enter_password(self, password):
        self.type(self.PASSWORD, password)
        return self
    
    def click_login(self):
        self.click(self.LOGIN_BTN)
        return self

# Usage - method chaining
(LoginPage(driver)
    .navigate()
    .enter_username("user")
    .enter_password("pass")
    .click_login())
```

#### C#
```csharp
public class LoginPage : BasePage
{
    public LoginPage EnterUsername(string username)
    {
        Type(Username, username);
        return this;  // Enable chaining
    }
    
    public LoginPage EnterPassword(string password)
    {
        Type(Password, password);
        return this;
    }
    
    public LoginPage ClickLogin()
    {
        Click(LoginButton);
        return this;
    }
}

// Usage - method chaining
new LoginPage(driver)
    .Navigate()
    .EnterUsername("user")
    .EnterPassword("pass")
    .ClickLogin();
```

**Key differences:**
- Python: `return self` → C#: `return this;`
- Python: `snake_case` → C#: `PascalCase`
- Python: No `new` → C#: `new LoginPage(driver)`

---

### 6. WRAPPER PATTERN (Element)

#### Python
```python
class Element:
    def __init__(self, driver, locator):
        self.driver = driver
        self.locator = locator
    
    @property
    def webelement(self):
        """Get fresh element each time"""
        return self.driver.find_element(*self.locator)
    
    def click(self):
        self.webelement.click()
        return self
    
    @property
    def text(self):
        return self.webelement.text
```

#### C#
```csharp
public class Element
{
    private readonly IWebDriver _driver;
    private readonly By _locator;
    
    public Element(IWebDriver driver, By locator)
    {
        _driver = driver;
        _locator = locator;
    }
    
    // Expression-bodied property - gets fresh element each time
    private IWebElement WebElement => _driver.FindElement(_locator);
    
    public Element Click()
    {
        WebElement.Click();
        return this;
    }
    
    public string Text => WebElement.Text;
}
```

**Key differences:**
- Python: `@property` → C#: `=> expression` (expression-bodied property)
- Python: `*self.locator` unpacking → C#: Direct `By` object
- Both achieve same goal: fresh element on each access!

---

### 7. CUSTOM EXCEPTIONS

#### Python
```python
class ElementNotInteractableError(Exception):
    """Custom exception for non-interactable elements"""
    pass

class PageNotLoadedError(Exception):
    """Custom exception for page load failures"""
    pass

# Usage
raise ElementNotInteractableError("Button is not clickable")
```

#### C#
```csharp
public class ElementNotInteractableException : Exception
{
    public ElementNotInteractableException(string message) : base(message)
    {
    }
}

public class PageNotLoadedException : Exception
{
    public PageNotLoadedException(string message) : base(message)
    {
    }
}

// Usage
throw new ElementNotInteractableException("Button is not clickable");
```

**Key differences:**
- Python: Inherit from `Exception` → C#: `: Exception`
- Python: `pass` → C#: Call `: base(message)`
- Python convention: `Error` suffix → C#: `Exception` suffix

---

### 8. TEST STRUCTURE

#### Python (pytest)
```python
import pytest

@pytest.fixture
def driver():
    driver = DriverFactory.create_driver(BrowserType.CHROME)
    yield driver
    driver.quit()

def test_login(driver):
    """Test login functionality"""
    login_page = LoginPage(driver)
    login_page.navigate().login("user", "pass")
    assert "dashboard" in driver.current_url

@pytest.mark.parametrize("username,password", [
    ("user1", "pass1"),
    ("user2", "pass2")
])
def test_multiple_users(driver, username, password):
    LoginPage(driver).login(username, password)
```

#### C# (NUnit)
```csharp
using NUnit.Framework;

[TestFixture]
public class LoginTests
{
    private IWebDriver _driver;
    
    [SetUp]
    public void Setup()
    {
        _driver = DriverFactory.CreateDriver(BrowserType.Chrome);
    }
    
    [Test]
    public void TestLogin()
    {
        var loginPage = new LoginPage(_driver);
        loginPage.Navigate().Login("user", "pass");
        Assert.That(_driver.Url, Does.Contain("dashboard"));
    }
    
    [TestCase("user1", "pass1")]
    [TestCase("user2", "pass2")]
    public void TestMultipleUsers(string username, string password)
    {
        new LoginPage(_driver).Login(username, password);
    }
    
    [TearDown]
    public void TearDown()
    {
        _driver?.Quit();
    }
}
```

**Key differences:**
- Python: `@pytest.fixture` → C#: `[SetUp]`
- Python: `yield` → C#: `[TearDown]`
- Python: `def test_*` → C#: `[Test] public void Test*()`
- Python: `@pytest.mark.parametrize` → C#: `[TestCase]`
- Python: `assert` → C#: `Assert.That()`

---

## Quick Reference Table

| Feature | Python | C# |
|---------|--------|-----|
| **Return self** | `return self` | `return this;` |
| **Constructor** | `__init__(self)` | `ClassName() { }` |
| **Private field** | `_field` (convention) | `private _field` |
| **Property** | `@property` | `PropName => expr;` |
| **Interface** | `ABC` + `@abstractmethod` | `interface IName` |
| **Static method** | `@staticmethod` | `static ReturnType Method()` |
| **Inheritance** | `super().__init__()` | `: base()` |
| **Create object** | `obj = MyClass()` | `var obj = new MyClass();` |
| **String type hint** | `name: str` | `string name` |
| **Test decorator** | `@pytest.fixture` | `[SetUp]` |
| **Locator** | `(By.ID, "id")` | `By.Id("id")` |

---

## Interview Quick Tips

### If asked "How do you implement X in C#?"

1. **Start with the pattern name**: "I'd use the [Pattern] pattern..."
2. **Explain why (Python knowledge!)**: "Because it solves [annoying problem]..."
3. **Then show C# syntax**: "In C#, this looks like..."

### Example:
> **Q: How do you avoid StaleElementReferenceException?**

**Answer:**
"I use the **Wrapper pattern** with an Element class, because caching elements causes staleness when the DOM updates. 

In C#, I create a class with a property that re-finds the element each time:

```csharp
private IWebElement WebElement => _driver.FindElement(_locator);
```

The expression-bodied property syntax means it's calculated fresh on every access, preventing stale references. The pattern is identical to Python's `@property`, just different syntax."

---

## You've Got This! 🎯

Remember: **95% is the same thinking, just 5% different syntax**. Your Python knowledge translates directly - just swap the words!
