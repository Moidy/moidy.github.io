# Selenium C# Framework - Organized Structure

## 📁 Project Structure

This is a **production-ready** Selenium framework demonstrating best practices for enterprise test automation. Each class is separated into its own file with proper namespacing.

```
organized/
├── Core/                           # Core framework components
│   ├── Config.cs                  # Singleton configuration manager
│   ├── DriverFactory.cs           # Factory for WebDriver creation
│   └── Exceptions/                # Custom exceptions
│       ├── ElementNotInteractableException.cs
│       └── PageNotLoadedException.cs
│
├── Strategies/                    # Strategy pattern implementations
│   ├── Browser/                   # Browser-specific strategies
│   │   ├── IBrowserStrategy.cs   # Browser strategy interface
│   │   ├── ChromeStrategy.cs     # Chrome configuration
│   │   ├── FirefoxStrategy.cs    # Firefox configuration
│   │   └── EdgeStrategy.cs       # Edge configuration
│   │
│   └── Wait/                      # Wait condition strategies
│       ├── IWaitStrategy.cs      # Wait strategy interface
│       ├── PresenceWait.cs       # Wait for element presence
│       ├── VisibilityWait.cs     # Wait for element visibility
│       └── ClickableWait.cs      # Wait for element to be clickable
│
├── Pages/                         # Page Object Model
│   ├── BasePage.cs               # Base class for all pages
│   └── LoginPage.cs              # Login page implementation
│
├── Elements/                      # Element wrappers
│   └── Element.cs                # Element wrapper to prevent stale references
│
└── Tests/                         # Test suites
    ├── LoginTests.cs             # Login functionality tests
    ├── ConfigTests.cs            # Configuration tests
    ├── StrategyTests.cs          # Strategy pattern tests
    └── ElementWrapperTests.cs    # Element wrapper tests
```

---

## 🎯 Design Patterns Implemented

### 1. **Singleton Pattern** (`Config.cs`)
- **Purpose**: Single source of truth for configuration
- **Benefits**: 
  - One place to change settings
  - Thread-safe with `Lazy<T>`
  - Memory efficient

### 2. **Factory Pattern** (`DriverFactory.cs`)
- **Purpose**: Centralized WebDriver creation
- **Benefits**:
  - Consistent driver setup
  - Easy to add new browsers
  - Encapsulates complex initialization

### 3. **Strategy Pattern** (`Strategies/`)
- **Purpose**: Swappable algorithms for browsers and waits
- **Benefits**:
  - Open/Closed principle (extend without modifying)
  - Different behavior without if/else chains
  - Easy to test each strategy

### 4. **Page Object Model** (`Pages/`)
- **Purpose**: Encapsulate page structure and behavior
- **Benefits**:
  - DRY - change locators once
  - Readable tests (business language)
  - Separation of concerns

### 5. **Fluent Interface** (`LoginPage.cs`)
- **Purpose**: Method chaining for readable test code
- **Benefits**:
  - Natural language flow
  - Less verbose
  - Easy to follow test logic

### 6. **Wrapper Pattern** (`Element.cs`)
- **Purpose**: Prevent stale element references
- **Benefits**:
  - Fresh element on each access
  - Enhanced API
  - Centralized error handling

---

## 🚀 Getting Started

### Prerequisites

```bash
dotnet add package Selenium.WebDriver
dotnet add package Selenium.Support
dotnet add package DotNetSeleniumExtras.WaitHelpers
dotnet add package NUnit
dotnet add package NUnit3TestAdapter
```

### Driver Setup

Download the appropriate WebDriver:
- **ChromeDriver**: https://chromedriver.chromium.org/
- **GeckoDriver** (Firefox): https://github.com/mozilla/geckodriver/releases
- **EdgeDriver**: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

Place drivers in your PATH or project folder.

---

## 💡 Usage Examples

### Basic Login Test

```csharp
[Test]
public void TestLogin()
{
    var config = Config.Instance;
    config.BaseUrl = "https://www.saucedemo.com";
    
    var driver = DriverFactory.CreateDriver(BrowserType.Chrome);
    var loginPage = new LoginPage(driver);
    
    loginPage
        .Navigate()
        .Login("standard_user", "secret_sauce");
    
    Assert.IsTrue(driver.Url.Contains("inventory.html"));
    driver.Quit();
}
```

### Using Different Wait Strategies

```csharp
// Wait for element to exist in DOM
var presenceWait = new PresenceWait();
var element1 = presenceWait.Wait(driver, By.Id("myElement"));

// Wait for element to be visible
var visibilityWait = new VisibilityWait();
var element2 = visibilityWait.Wait(driver, By.Id("myElement"));

// Wait for element to be clickable
var clickableWait = new ClickableWait();
var element3 = clickableWait.Wait(driver, By.Id("myButton"));
```

### Using Element Wrapper

```csharp
var username = new Element(driver, By.Id("username"));
var password = new Element(driver, By.Id("password"));
var loginBtn = new Element(driver, By.Id("login"));

username.WaitUntilVisible().Type("testuser");
password.WaitUntilVisible().Type("password123");
loginBtn.WaitUntilClickable().Click();
```

---

## 🧪 Running Tests

### Run All Tests
```bash
dotnet test
```

### Run Specific Category
```bash
dotnet test --filter TestCategory=Smoke
dotnet test --filter TestCategory=Strategy
dotnet test --filter TestCategory=Wrapper
```

### Run Specific Test Class
```bash
dotnet test --filter ClassName=LoginTests
```

---

## 📚 Test Categories

| Category | Description | Files |
|----------|-------------|-------|
| **Smoke** | Critical path tests | `LoginTests.cs` |
| **Negative** | Error handling tests | `LoginTests.cs` |
| **UI** | User interface tests | `LoginTests.cs` |
| **Unit** | Unit tests for framework components | `ConfigTests.cs` |
| **Strategy** | Strategy pattern demonstration | `StrategyTests.cs` |
| **Wrapper** | Element wrapper tests | `ElementWrapperTests.cs` |

---

## 🎓 Interview Tips

### When Discussing This Framework:

1. **Singleton Config**
   - "We use Singleton with Lazy<T> for thread-safe, lazy-loaded configuration"
   - "Single source of truth prevents config scattered across test files"

2. **Factory + Strategy**
   - "Factory creates drivers, Strategy handles browser-specific configuration"
   - "Adding a new browser means one new Strategy class, not editing 50 tests"

3. **Page Object Model**
   - "Locators live in page classes, not test files"
   - "Change a button ID once in LoginPage, all tests automatically updated"

4. **Fluent Interface**
   - "Tests read like user stories: Navigate().Login().Verify()"
   - "return this enables method chaining"

5. **Element Wrapper**
   - "Prevents StaleElementReferenceException by fetching fresh element each time"
   - "Adds enhanced API (WaitUntilVisible, Click with JavaScript fallback)"

### Common Interview Questions:

**Q: Why is Config sealed?**
- "Prevents subclassing which would break Singleton pattern"

**Q: Why use Strategy pattern for waits?**
- "Different elements need different waits. Strategy avoids if/else chains and follows Open/Closed principle"

**Q: How do you handle stale elements?**
- "Element wrapper always fetches fresh reference via property"

**Q: What's the benefit of BasePage?**
- "DRY - common methods defined once, inherited by all pages"

---

## 🔧 Configuration

### Change Browser

```csharp
var config = Config.Instance;
config.Browser = BrowserType.Firefox;  // Chrome, Firefox, Edge
```

### Run Headless

```csharp
config.Headless = true;
```

### Change Environment

```csharp
config.LoadFromEnvironment("staging");  // dev, staging, prod
```

### Adjust Timeouts

```csharp
config.ImplicitWait = 10;      // seconds
config.ExplicitWait = 15;      // seconds
config.PageLoadTimeout = 30;   // seconds
```

---

## 📖 Key Differences from Python

| Feature | Python | C# |
|---------|--------|-----|
| **Singleton** | `__new__` method | `Lazy<T>` pattern |
| **Interface** | `ABC` abstract class | `interface` keyword |
| **Method Chaining** | `return self` | `return this;` |
| **Properties** | `@property` decorator | Expression-bodied property `=>` |
| **Attributes** | `@decorator` | `[Attribute]` |
| **Constructor** | `__init__(self)` | `ClassName()` |
| **Locators** | `(By.ID, "id")` | `By.Id("id")` |
| **Test Framework** | pytest | NUnit |

---

## 🚨 Common Mistakes to Avoid

1. **Don't instantiate Config directly**
   ```csharp
   // ❌ Wrong
   var config = new Config();
   
   // ✅ Correct
   var config = Config.Instance;
   ```

2. **Don't cache IWebElement**
   ```csharp
   // ❌ Wrong - stale reference risk
   var element = driver.FindElement(By.Id("username"));
   element.Click();
   // ... time passes ...
   element.SendKeys("text");  // Might be stale!
   
   // ✅ Correct - use Element wrapper
   var element = new Element(driver, By.Id("username"));
   element.Click();
   element.Type("text");  // Always fresh
   ```

3. **Don't duplicate waits in tests**
   ```csharp
   // ❌ Wrong
   var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
   wait.Until(ExpectedConditions.ElementIsVisible(locator));
   
   // ✅ Correct - use Strategy
   var element = new VisibilityWait().Wait(driver, locator);
   ```

---

## 📝 Next Steps

1. **Add More Page Objects**: Create pages for Dashboard, Profile, Settings, etc.
2. **Data-Driven Tests**: Use `[TestCase]` or read from CSV/JSON
3. **Parallel Execution**: Configure NUnit for parallel test runs
4. **Reporting**: Add Extent Reports or Allure
5. **CI/CD Integration**: Set up GitHub Actions or Azure DevOps pipeline

---

## 🎯 Interview Prep Checklist

- [ ] Can explain Singleton pattern and why `sealed` is used
- [ ] Can describe Factory + Strategy combination
- [ ] Can implement fluent interface (`return this`)
- [ ] Can explain how Element wrapper prevents stale references
- [ ] Can discuss benefits of Page Object Model
- [ ] Can compare Python vs C# implementations
- [ ] Can add a new browser Strategy without modifying existing code
- [ ] Can add a new wait Strategy
- [ ] Can create new Page Object classes
- [ ] Can explain when to use each wait type (Presence, Visibility, Clickable)

---

## 💪 You've Got This!

This framework demonstrates **senior-level automation engineering** skills:
- ✅ Design patterns (6 different patterns)
- ✅ SOLID principles
- ✅ Clean, maintainable code
- ✅ Proper separation of concerns
- ✅ Production-ready structure

**Remember**: The patterns are the same between Python and C#. You already know the hard part! 🚀
