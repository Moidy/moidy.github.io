# C# Selenium Framework - Design Patterns

Complete C# port of the Python Selenium framework patterns for interview preparation.

## Files

- **FrameworkPatterns.cs** - Complete C# implementation of all design patterns
- **SENIOR_AUTOMATION_QUIZ_CSHARP.md** - C# version of the quiz with C#-specific answers

## Quick Comparison: Python → C#

### Pattern Implementation Differences

| Pattern | Python Key Concept | C# Key Concept |
|---------|-------------------|----------------|
| **Singleton** | `__new__` with class variable | `Lazy<T>` for thread safety |
| **Factory** | Static methods | Static class with dictionary |
| **Strategy** | ABC + `@abstractmethod` | `interface` keyword |
| **Page Object** | `__init__(self, driver)` | Constructor with `: base(driver)` |
| **Fluent** | `return self` | `return this;` |
| **Wrapper** | `@property` | Expression-bodied property `=>` |
| **Decorator** | `@decorator` syntax | `[Attribute]` or `ITestAction` |

### Syntax Quick Reference

```python
# Python
class BasePage:
    def __init__(self, driver):
        self.driver = driver
    
    def click(self, locator):
        self.driver.find_element(*locator).click()
        return self
```

```csharp
// C#
public class BasePage
{
    protected IWebDriver Driver;
    
    public BasePage(IWebDriver driver)
    {
        Driver = driver;
    }
    
    public BasePage Click(By locator)
    {
        Driver.FindElement(locator).Click();
        return this;
    }
}
```

## Key C# Specific Points

### 1. Lazy Initialization (Singleton)
```csharp
private static readonly Lazy<Config> _instance = 
    new Lazy<Config>(() => new Config());
```
- Thread-safe by default
- No need for locks or double-check locking
- Equivalent to Python's `__new__` pattern

### 2. Expression-Bodied Members
```csharp
private IWebElement WebElement => _driver.FindElement(_locator);
```
- Short syntax for properties
- Calculated on each access (not cached)
- Perfect for Element wrapper pattern

### 3. NUnit Attributes vs Pytest Fixtures
```csharp
[TestFixture]
public class Tests
{
    [SetUp]     // Like pytest fixture with autouse=True
    public void Setup() { }
    
    [TearDown]  // Like yield in fixture
    public void TearDown() { }
    
    [Test]      // Like def test_something()
    public void TestSomething() { }
}
```

### 4. Interface vs ABC
```csharp
// C# interface - cleaner than Python ABC
public interface IWaitStrategy
{
    IWebElement Wait(IWebDriver driver, By locator, int timeout);
}

public class ClickableWait : IWaitStrategy
{
    public IWebElement Wait(IWebDriver driver, By locator, int timeout)
    {
        // Implementation
    }
}
```

### 5. Properties vs Methods
```csharp
// C# properties (no parentheses when accessing)
public string CurrentUrl => Driver.Url;
public string Title => Driver.Title;

// Usage:
string url = page.CurrentUrl;  // Not page.CurrentUrl()
```

## What Stays The Same (95%)

✅ **All pattern concepts and "why" reasoning**
- Singleton solves scattered config
- Factory encapsulates driver creation
- Strategy allows swappable wait behavior
- Page Object centralizes locators
- Fluent makes tests readable
- Wrapper prevents stale elements

✅ **All architectural decisions**
- When to use each pattern
- How to structure framework folders
- Configuration management approach
- Test organization principles

✅ **All code smell identification**
- Duplicate locators
- If/else chains for wait types
- Cached elements causing stale references
- Missing waits
- Poor separation of concerns

## Major Differences to Learn

### 1. Naming Conventions
- Python: `snake_case` → C#: `PascalCase`
- Python: `_private` → C#: `private _field`
- Python: `def method_name()` → C#: `public ReturnType MethodName()`

### 2. Type System
- Python: Duck typing, optional hints → C#: Strong static typing
- Python: `def click(self, locator)` → C#: `public BasePage Click(By locator)`

### 3. Locators
- Python: `(By.ID, "username")` → C#: `By.Id("username")`
- Python: `*locator` unpacking → C#: Direct `By` object

### 4. Test Frameworks
- Pytest: Function-based, fixtures → NUnit: Class-based, attributes
- Pytest: `@pytest.fixture` → NUnit: `[SetUp]` attribute
- Pytest: `def test_*` → NUnit: `[Test]` on methods

## Interview Focus Areas

### Questions You'll Get Asked

1. **"How do you implement Singleton in C#?"**
   - Answer: `Lazy<T>` for thread-safe lazy init
   - Show you know thread safety matters

2. **"How do you avoid StaleElementReferenceException?"**
   - Answer: Element wrapper with property
   - Show code: `private IWebElement WebElement => _driver.FindElement(_locator);`

3. **"How do you handle retries in C#?"**
   - Answer: Custom NUnit attribute implementing `IWrapSetUpTearDown`
   - Or mention Polly library for production

4. **"Explain POM in your framework"**
   - Answer: BasePage with common methods, specific pages inherit
   - Locators as `private static readonly By`
   - Return `this` for fluent interface

5. **"How do you switch between environments?"**
   - Answer: Singleton Config + JSON files
   - Environment variables or `.runsettings` file

## Quick Study Plan

### Day 1: Syntax Familiarity
- Read through FrameworkPatterns.cs
- Note Python → C# syntax differences
- Practice writing classes, methods, properties

### Day 2: Pattern Implementation
- Implement Singleton with `Lazy<T>`
- Create Factory with Strategy
- Build BasePage with fluent interface

### Day 3: Advanced Patterns
- Element wrapper with properties
- Custom NUnit attributes
- Wait strategies with interfaces

### Day 4: Quiz Practice
- Go through SENIOR_AUTOMATION_QUIZ_CSHARP.md
- Write answers without looking
- Focus on explaining "why" not just "how"

### Day 5: Mock Interview
- Explain each pattern to yourself out loud
- Justify pattern choices for scenarios
- Practice whiteboarding classes

## Common Pitfalls to Avoid

❌ **Saying "return self" in C# interview** → Say "`return this;`"
❌ **Calling properties with parentheses** → `page.Title` not `page.Title()`
❌ **Using Python naming** → `clickButton()` not `click_button()`
❌ **Forgetting access modifiers** → `public`, `private`, `protected` required
❌ **Comparing to pytest incorrectly** → Know NUnit's attribute system

## You're 95% Ready!

Remember: **The patterns and reasoning are identical**. The syntax is just different clothing on the same body.

When asked "How would you solve X?", your Python knowledge translates directly:
- Scattered config → Singleton
- Complex setup → Factory
- Multiple wait types → Strategy
- Duplicate locators → Page Object
- Stale elements → Wrapper

Just express it in C# syntax, and you're golden! 🚀
