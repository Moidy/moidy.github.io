# Senior Automation Engineer Quiz - C# Edition
## Design Patterns & Framework Architecture

---

### Section 1: Pattern Identification (20 points)

**Q1.** You have 83 test files with hardcoded URLs. When the staging URL changes, you need to update all 83 files. Which pattern solves this, and what's the key technical principle?

<details>
<summary>Answer</summary>

**Pattern:** Singleton Pattern (Config class)

**Technical Principle:** Single source of truth - one instance holds configuration, accessible globally without creating multiple copies.

**Implementation in C#:**
```csharp
public sealed class Config
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    private Config() { } // Private constructor
}
```

`Lazy<T>` provides thread-safe lazy initialization in C#, similar to Python's `__new__` pattern.
</details>

---

**Q2.** Your BasePage has this code:
```csharp
public IWebElement FindElement(By locator, string waitType)
{
    if (waitType == "clickable")
        return new WebDriverWait(Driver, TimeSpan.FromSeconds(10))
            .Until(ExpectedConditions.ElementToBeClickable(locator));
    else if (waitType == "visible")
        return new WebDriverWait(Driver, TimeSpan.FromSeconds(10))
            .Until(ExpectedConditions.ElementIsVisible(locator));
    else if (waitType == "presence")
        return new WebDriverWait(Driver, TimeSpan.FromSeconds(10))
            .Until(ExpectedConditions.ElementExists(locator));
}
```
What pattern should replace this? Why is the current approach a code smell?

<details>
<summary>Answer</summary>

**Pattern:** Strategy Pattern

**Why it's a code smell:**
- Violates Open/Closed Principle (must modify method to add new wait types)
    - open/closed policy being: open for extension, closed for modification
    - this policy is violated because adding a new wait type requires modifying the existing method
- Hard to test individual wait strategies
- String parameters are error-prone (typos, no IntelliSense)
- Will grow into unmaintainable if/else chain

**Better approach:**
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

// Usage: FindElement(locator, new ClickableWait())
```

**C# specific benefits:**
- Interface provides compile-time type safety
- IntelliSense shows available strategies
- Can use dependency injection
</details>

---

**Q3.** You need to add screenshot capture to 50 test methods when they fail. You don't want to modify the test code itself. What's the C# equivalent of Python decorators?

<details>
<summary>Answer</summary>

**Pattern:** In C#, use **NUnit Attributes** or **Aspect-Oriented Programming (AOP)**

**NUnit approach (most common):**
```csharp
[AttributeUsage(AttributeTargets.Method)]
public class ScreenshotOnFailureAttribute : NUnitAttribute, ITestAction
{
    public void BeforeTest(ITest test) { }
    
    public void AfterTest(ITest test)
    {
        if (TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Failed)
        {
            var driver = // Get driver from test context
            driver.GetScreenshot().SaveAsFile($"failure_{test.Name}.png");
        }
    }
    
    public ActionTargets Targets => ActionTargets.Test;
}

// Usage:
[Test, ScreenshotOnFailure]
public void TestLogin()
{
    // Test code - no try/catch needed
}
```

**Alternative - Use [TearDown] with TestContext:**
```csharp
[TearDown]
public void TearDown()
{
    if (TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Failed)
    {
        _driver.GetScreenshot().SaveAsFile($"failure_{TestContext.CurrentContext.Test.Name}.png");
    }
}
```

**Why:**
- Non-invasive: adds behavior without modifying test method
- C# attributes are declarative like Python decorators
- TestContext provides access to test execution state
</details>

---

### Section 2: Code Review (30 points)

**Q4.** Review this code. Identify at least 3 issues and suggest improvements:

```csharp
public class LoginPage : IWebDriver
{
    By USERNAME = By.Id("username");
    By PASSWORD = By.Id("password");  
    By LOGIN_BTN = By.Id("login");
    
    public void login(string user, string pwd, IWebDriver driver)
    {
        this.Type(USERNAME_INPUT, user);
        this.Type(PASSWORD_INPUT, pwd);
        this.Click(LOGIN_BUTTON, new ClickableWait());
    }
}
```

<details>
<summary>Answer</summary>

**Issues:**

1. **Invalid inheritance:** `LoginPage : IWebDriver` - can't implement IWebDriver directly, should inherit from BasePage
2. **No driver stored:** No constructor or field to store driver reference, so `Type()` and `Click()` have no driver to work with
3. **No waits:** Without BasePage inheritance, there's no wait mechanism
4. **Inconsistent naming:** 
   - C# convention: PascalCase for public methods (`login` should be `Login`)
   - Defines `USERNAME` but uses `USERNAME_INPUT`
   - Defines `LOGIN_BTN` but uses `LOGIN_BUTTON`
5. **Non-readonly locators:** Locators should be `private static readonly` or constants
6. **Driver passed as parameter:** Driver should be stored in constructor, not passed to every method
7. **No return type:** Method is `void`, can't support fluent interface

**Improved version:**
```csharp
public class LoginPage : BasePage
{
    // Locators as private static readonly (C# convention)
    private static readonly By UsernameInput = By.Id("username");
    private static readonly By PasswordInput = By.Id("password");
    private static readonly By LoginButton = By.Id("login");
    
    public LoginPage(IWebDriver driver) : base(driver)
    {
        // BasePage stores driver and sets up waits
    }
    
    public LoginPage Login(string user, string password)
    {
        // Type() and Click() inherited from BasePage
        // They include built-in wait strategies
        Type(UsernameInput, user);     // BasePage.Type() waits for visibility
        Type(PasswordInput, password);
        Click(LoginButton, new ClickableWait());  // Explicit clickable wait
        return this;  // Fluent interface - return this in C#
    }
}
```

**C# specific improvements:**
- PascalCase method names (C# convention)
- `private static readonly` for locators (compile-time optimization)
- Base constructor call with `: base(driver)`
- Return `LoginPage` type for fluent interface
</details>

---

**Q5.** This Element wrapper has a bug. What is it and how do you fix it?

```csharp
public class Element
{
    private IWebDriver _driver;
    private By _locator;
    private IWebElement _element;
    
    public Element(IWebDriver driver, By locator)
    {
        _driver = driver;
        _locator = locator;
        _element = driver.FindElement(locator);
    }
    
    public void Click()
    {
        _element.Click();
    }
    
    public void Type(string text)
    {
        _element.SendKeys(text);
    }
}
```

<details>
<summary>Answer</summary>

**Bug:** Element is found once in constructor and cached. If the page changes or element is re-rendered, you'll get `StaleElementReferenceException`.

**Fix:** Use a property to re-find element on each access:

```csharp
public class Element
{
    private readonly IWebDriver _driver;
    private readonly By _locator;
    
    public Element(IWebDriver driver, By locator)
    {
        _driver = driver;
        _locator = locator;
        // Don't find element here!
    }
    
    // Property provides fresh element each time
    private IWebElement WebElement => _driver.FindElement(_locator);
    
    public Element Click()
    {
        WebElement.Click();  // Always fresh
        return this;         // Fluent interface
    }
    
    public Element Type(string text)
    {
        WebElement.SendKeys(text);
        return this;
    }
    
    public string Text => WebElement.Text;
}
```

**C# specific notes:**
- `=>` expression-bodied property (shorthand for getter)
- `readonly` fields prevent accidental modification
- Return `Element` type (not `void`) for fluent interface
- Property calculated on each access, not cached
</details>

---

### Section 3: Architecture Decisions (30 points)

**Q6.** Your team has 3 environments (dev, staging, prod) with different URLs, timeouts, and browser settings. How do you design the configuration system in C#? Include:
- Pattern choice and why
- How to switch between environments
- Where config values are stored
- How tests access config

<details>
<summary>Answer</summary>

**Pattern:** Singleton + Configuration Manager

**Design:**

```csharp
using System.Configuration;
using Newtonsoft.Json;

public sealed class Config
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    public string BaseUrl { get; private set; }
    public int Timeout { get; private set; }
    public BrowserType Browser { get; private set; }
    
    private Config()
    {
        LoadFromEnvironment();
    }
    
    private void LoadFromEnvironment()
    {
        // Read from environment variable
        string env = Environment.GetEnvironmentVariable("TEST_ENV") ?? "dev";
        string configFile = $"config.{env}.json";
        
        // Load JSON config file
        var json = File.ReadAllText(configFile);
        var settings = JsonConvert.DeserializeObject<ConfigSettings>(json);
        
        BaseUrl = settings.BaseUrl;
        Timeout = settings.Timeout;
        Browser = settings.Browser;
    }
}

public class ConfigSettings
{
    public string BaseUrl { get; set; }
    public int Timeout { get; set; }
    public BrowserType Browser { get; set; }
}
```

**Storage:** JSON files per environment
```json
// config.dev.json
{
  "BaseUrl": "https://dev.example.com",
  "Timeout": 10,
  "Browser": "Chrome"
}
```

**Environment switching:**
```cmd
set TEST_ENV=staging
dotnet test
```

Or in `.runsettings`:
```xml
<RunConfiguration>
  <EnvironmentVariables>
    <TEST_ENV>staging</TEST_ENV>
  </EnvironmentVariables>
</RunConfiguration>
```

**Test access:**
```csharp
var config = Config.Instance;  // Always same instance
string url = config.BaseUrl;
```

**Why:**
- `Lazy<T>` provides thread-safe singleton
- Environment variables for easy CI/CD integration
- JSON.NET for clean config file parsing
- No hardcoded values in tests
</details>

---

**Q7.** You need to support Chrome, Firefox, and Edge with different options for each. Some tests need headless, some don't. Design the driver creation system using both Factory and Strategy patterns.

<details>
<summary>Answer</summary>

**Pattern:** Factory Pattern + Strategy Pattern

**Design:**

```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Firefox;
using OpenQA.Selenium.Edge;

// Strategy Pattern - Different browser configuration strategies
public interface IBrowserStrategy
{
    IWebDriver CreateDriver(bool headless);
}

public class ChromeStrategy : IBrowserStrategy
{
    public IWebDriver CreateDriver(bool headless)
    {
        var options = new ChromeOptions();
        options.AddArgument("--no-sandbox");
        options.AddArgument("--disable-dev-shm-usage");
        options.AddArgument("--window-size=1920,1080");
        
        if (headless)
            options.AddArgument("--headless=new");
        
        return new ChromeDriver(options);
    }
}

public class FirefoxStrategy : IBrowserStrategy
{
    public IWebDriver CreateDriver(bool headless)
    {
        var options = new FirefoxOptions();
        options.AddArgument("--width=1920");
        options.AddArgument("--height=1080");
        
        if (headless)
            options.AddArgument("--headless");
        
        return new FirefoxDriver(options);
    }
}

public class EdgeStrategy : IBrowserStrategy
{
    public IWebDriver CreateDriver(bool headless)
    {
        var options = new EdgeOptions();
        options.AddArgument("--no-sandbox");
        
        if (headless)
            options.AddArgument("--headless");
        
        return new EdgeDriver(options);
    }
}

// Factory Pattern - Creates appropriate strategy and driver
public enum BrowserType
{
    Chrome,
    Firefox,
    Edge
}

public static class DriverFactory
{
    private static readonly Dictionary<BrowserType, IBrowserStrategy> Strategies =
        new Dictionary<BrowserType, IBrowserStrategy>
        {
            { BrowserType.Chrome, new ChromeStrategy() },
            { BrowserType.Firefox, new FirefoxStrategy() },
            { BrowserType.Edge, new EdgeStrategy() }
        };
    
    public static IWebDriver CreateDriver(BrowserType browserType, bool headless = false)
    {
        if (!Strategies.ContainsKey(browserType))
            throw new ArgumentException($"Unsupported browser: {browserType}");
        
        var strategy = Strategies[browserType];
        return strategy.CreateDriver(headless);
    }
}
```

**NUnit fixture:**
```csharp
[TestFixture]
public class LoginTests
{
    private IWebDriver _driver;
    
    [SetUp]
    public void Setup()
    {
        // Read from TestContext or config
        var browser = TestContext.Parameters.Get("browser", "Chrome");
        var headless = TestContext.Parameters.Get("headless", "false") == "true";
        
        _driver = DriverFactory.CreateDriver(
            Enum.Parse<BrowserType>(browser, ignoreCase: true),
            headless
        );
    }
    
    [TearDown]
    public void TearDown()
    {
        _driver?.Quit();
    }
}
```

**Run with parameters:**
```cmd
dotnet test --TestParameters:browser=Firefox --TestParameters:headless=true
```

**Why Factory + Strategy:**
- **Factory:** Centralizes driver creation, manages strategy mapping
- **Strategy:** Each browser has its own configuration logic
- Dictionary-based mapping eliminates if/else chains
- Easy to add new browsers: create strategy, add to dictionary
- Type-safe with enums (no string typos)
</details>

---

**Q8.** Explain when you would use each wait approach in C# and why:

a) `Driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(10);`  
b) `new WebDriverWait(Driver, TimeSpan.FromSeconds(10)).Until(ExpectedConditions.ElementIsVisible(locator));`  
c) `Thread.Sleep(5000);`  
d) Custom wait condition with polling

<details>
<summary>Answer</summary>

**a) Implicit Wait:**
- **When:** Global fallback for simple scripts
- **Why:** Applied to all FindElement calls automatically
- **C# syntax:** `Driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(10);`
- **Downside:** Can't change timeout per element, not recommended for frameworks

**b) Explicit Wait (WebDriverWait):**
- **When:** Production framework (ALWAYS use this)
- **Why:** Specific timeout per action, intelligent polling, fails fast when condition met
- **C# syntax:** 
```csharp
var wait = new WebDriverWait(Driver, TimeSpan.FromSeconds(10));
wait.Until(ExpectedConditions.ElementToBeClickable(locator));
```
- **Example:** Waiting for element to be clickable before clicking

**c) Thread.Sleep():**
- **When:** ALMOST NEVER in production code
- **Only acceptable use:** Debugging/troubleshooting temporarily
- **C# syntax:** `Thread.Sleep(5000);` or `Task.Delay(5000).Wait();`
- **Why bad:** Wastes time (always waits full duration), not dynamic, not intelligent

**d) Custom Wait Condition:**
- **When:** Built-in ExpectedConditions don't cover your case
- **C# syntax:**
```csharp
var wait = new WebDriverWait(Driver, TimeSpan.FromSeconds(10));
wait.Until(d => d.FindElements(locator).Count == 5);  // Lambda expression
```
- **Example:** Wait for element count to equal 5, wait for CSS property value, wait for AJAX complete
- **Why:** Reusable, testable, same interface as built-in conditions

**Senior insight:** 
- Explicit waits are non-negotiable for production
- Implicit waits + explicit waits together can cause unexpected timeouts (they stack)
- C# lambda expressions make custom conditions very clean
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
DOM updates/re-renders after you've cached the IWebElement reference. Element pointer becomes invalid.

**Solutions:**

1. **Re-find element each time (no caching)**
   - Pro: Simple, always fresh
   - Con: Slower (extra FindElement operations)
   - Implementation: Don't store elements, always `Driver.FindElement()` when needed

2. **Element Wrapper with Property**
   - Pro: Transparent, clean API, always fresh
   - Con: Slight overhead
   - Implementation:
```csharp
public class Element
{
    private readonly IWebDriver _driver;
    private readonly By _locator;
    
    private IWebElement WebElement => _driver.FindElement(_locator);  // Fresh each time
    
    public void Click() => WebElement.Click();
}
```

3. **Retry attribute on test methods**
   - Pro: Handles stale + other transient errors
   - Con: Retries might hide real issues, slower on failures
   - Implementation:
```csharp
[Test, Retry(3)]
public void TestDynamicElement()
{
    // NUnit will retry entire test up to 3 times on failure
}
```

4. **Wait for staleness then re-find**
   - Pro: Explicit handling when you know re-render happens
   - Con: Requires knowing when to apply it
   - Implementation:
```csharp
wait.Until(ExpectedConditions.StalenessOf(element));
element = Driver.FindElement(locator);
```

**Best choice:** **Element Wrapper (#2)**
- Clean abstraction, always works
- No changes to test code
- Handles problem at framework level
- Small performance cost is worth reliability
- C# properties make this pattern very elegant

**Senior insight:** If you're seeing 30% failure rate, it's a framework problem, not a test problem. Fix it at the framework level once, not in 100 tests.
</details>

---

**Q10.** Design a retry mechanism in C# that:
- Retries on WebDriverTimeoutException and StaleElementReferenceException only
- Does NOT retry on AssertionException
- Logs each attempt
- Has configurable max attempts and delay
- Can be applied via NUnit attribute

<details>
<summary>Answer</summary>

```csharp
using System;
using System.Threading;
using NUnit.Framework;
using NUnit.Framework.Interfaces;
using OpenQA.Selenium;

[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
public class RetryOnExceptionsAttribute : NUnitAttribute, IWrapSetUpTearDown
{
    private readonly Type[] _retryableExceptions;
    private readonly int _maxAttempts;
    private readonly int _delayMs;

    public RetryOnExceptionsAttribute(
        int maxAttempts = 3, 
        int delayMs = 1000,
        params Type[] retryableExceptions)
    {
        _maxAttempts = maxAttempts;
        _delayMs = delayMs;
        _retryableExceptions = retryableExceptions ?? new[]
        {
            typeof(WebDriverTimeoutException),
            typeof(StaleElementReferenceException)
        };
    }

    public ActionTargets Targets => ActionTargets.Test;

    public TestResult Wrap(TestAction action)
    {
        Exception lastException = null;
        
        for (int attempt = 1; attempt <= _maxAttempts; attempt++)
        {
            try
            {
                TestContext.WriteLine($"Attempt {attempt}/{_maxAttempts}: {TestContext.CurrentContext.Test.Name}");
                
                var result = action.Invoke();
                
                TestContext.WriteLine($"Success on attempt {attempt}");
                return result;
            }
            catch (Exception ex)
            {
                bool isRetryable = false;
                foreach (var retryableType in _retryableExceptions)
                {
                    if (retryableType.IsInstanceOfType(ex))
                    {
                        isRetryable = true;
                        break;
                    }
                }

                if (!isRetryable)
                {
                    // Don't retry (e.g., AssertionException)
                    TestContext.WriteLine($"Non-retryable exception: {ex.GetType().Name}");
                    throw;
                }

                lastException = ex;
                TestContext.WriteLine($"Attempt {attempt} failed with {ex.GetType().Name}: {ex.Message}");
                
                if (attempt < _maxAttempts)
                {
                    TestContext.WriteLine($"Retrying in {_delayMs}ms...");
                    Thread.Sleep(_delayMs);
                }
                else
                {
                    TestContext.WriteLine($"All {_maxAttempts} attempts failed");
                }
            }
        }
        
        // If we get here, all retries failed
        throw lastException;
    }
}

// Usage:
[Test]
[RetryOnExceptions(
    maxAttempts: 3,
    delayMs: 2000,
    typeof(WebDriverTimeoutException),
    typeof(StaleElementReferenceException)
)]
public void TestFlakyElement()
{
    // Test that might have stale elements or timeouts
    var element = _driver.FindElement(By.Id("dynamic"));
    element.Click();
    Assert.That(_driver.Url, Does.Contain("success"));  // This won't be retried if it fails
}
```

**Alternative using Polly library (more robust):**
```csharp
using Polly;

public class TestBase
{
    protected void ExecuteWithRetry(Action testAction)
    {
        var policy = Policy
            .Handle<WebDriverTimeoutException>()
            .Or<StaleElementReferenceException>()
            .WaitAndRetry(
                retryCount: 3,
                sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)),
                onRetry: (exception, timespan, attempt, context) =>
                {
                    TestContext.WriteLine($"Retry {attempt} after {timespan.TotalSeconds}s due to {exception.GetType().Name}");
                }
            );
        
        policy.Execute(testAction);
    }
}

// Usage:
[Test]
public void TestWithPolly()
{
    ExecuteWithRetry(() =>
    {
        _driver.FindElement(By.Id("dynamic")).Click();
        Assert.That(_driver.Url, Does.Contain("success"));
    });
}
```

**Key points:**
- Custom NUnit attribute implements `IWrapSetUpTearDown`
- Type checking for retryable exceptions (compile-time safe)
- Other exceptions (AssertionException) propagate immediately
- TestContext.WriteLine for debugging
- Polly library provides production-grade retry policies
</details>

---

## Scoring Guide

- **18-20 points:** Senior level - Ready for senior C# automation roles
- **15-17 points:** Mid-Senior level - Solid understanding, minor gaps
- **12-14 points:** Mid level - Good foundation, needs more pattern practice
- **Below 12:** Junior-Mid level - Focus on C# framework design patterns

---

## Key C# vs Python Differences Summary

| Concept | Python | C# |
|---------|--------|-----|
| **Fluent return** | `return self` | `return this;` |
| **Singleton** | `__new__` method | `Lazy<T>` or static readonly |
| **Decorator** | `@decorator` | `[Attribute]` or AOP |
| **Interface** | `ABC` + `@abstractmethod` | `interface` keyword |
| **Constructor** | `__init__` | Same name as class |
| **Property** | `@property` | `prop => expression;` |
| **Naming** | snake_case | PascalCase |
| **Test framework** | pytest | NUnit/MSTest/xUnit |
| **Locators** | tuple `(By.ID, "id")` | `By.Id("id")` |
| **Private fields** | `_field` convention | `_field` with `private` |

---

## Study Recommendations

### Key C# topics to master:
1. **Interfaces** - Used heavily in Strategy pattern
2. **Properties** - Expression-bodied properties for Element wrapper
3. **Lazy<T>** - Thread-safe singleton implementation
4. **LINQ** - Useful for collection operations in tests
5. **NUnit/MSTest** - Test framework attributes and lifecycle
6. **async/await** - For modern C# async operations
7. **Dependency Injection** - Optional but common in enterprise frameworks

### Practice:
1. Port your Python Page Objects to C#
2. Implement each pattern from scratch in C#
3. Learn NUnit attribute system (similar to pytest fixtures)
4. Practice with Visual Studio debugger
