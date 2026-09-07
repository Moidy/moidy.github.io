# C# Class Modifiers Reference Guide
## For Python Developers Learning C#

---

## Overview

C# has several class modifiers that don't exist in Python. Understanding these is critical for Selenium framework design and interviews.

---

## Class Access Modifiers

### `public` - Accessible from Anywhere

```csharp
public class LoginPage 
{
    // Any code in any assembly can use this class
}
```

**Usage:** Most page objects and utility classes  
**Python equivalent:** All classes are public by default

---

### `internal` - Accessible Only Within Same Assembly/Project

```csharp
internal class Helper 
{
    // Only code in this project can use this class
}
```

**Usage:** Framework internals you don't want exposed  
**Default:** If you don't specify an access modifier, class is `internal`  
**Python equivalent:** No direct equivalent (module privacy is by convention)

---

### `private` - Only for Nested Classes

```csharp
public class Outer 
{
    private class Inner 
    {
        // Only Outer class can see and use Inner
    }
}
```

**Usage:** Helper classes that should only be used by the containing class  
**Python equivalent:** Nested class with `_` prefix by convention

---

## Class Type Modifiers

### `sealed` - Cannot Be Inherited (Final)

```csharp
public sealed class Config 
{
    // No one can inherit from Config
    // Prevents: public class MyConfig : Config { }
}
```

**When to use:**
- ✅ **Singleton classes** - Prevent inheritance from breaking the pattern
- ✅ **Utility classes** - When extension makes no sense
- ✅ **Performance** - Slight optimization (compiler knows no subclasses)

**Python equivalent:** No direct equivalent, convention only

**Interview answer:**
> "I use `sealed` on Singleton classes to prevent inheritance that could break the pattern by creating multiple instances through a subclass."

---

### `abstract` - Cannot Be Instantiated, Must Be Inherited

```csharp
public abstract class BasePage 
{
    // Can't do: new BasePage()
    // Must do: new LoginPage() where LoginPage : BasePage
    
    public abstract void Navigate();  // Subclass must implement
    
    public void Click(By locator)     // Subclass can use
    {
        // Implementation
    }
}

public class LoginPage : BasePage
{
    public override void Navigate()
    {
        // Must provide implementation
    }
}
```

**When to use:**
- ✅ **Base classes** that shouldn't be instantiated directly
- ✅ **Defining contracts** that subclasses must implement
- ✅ **Shared functionality** with required customization points

**Python equivalent:** `ABC` (Abstract Base Class) from `abc` module

```python
# Python equivalent
from abc import ABC, abstractmethod

class BasePage(ABC):
    @abstractmethod
    def navigate(self):
        pass
    
    def click(self, locator):
        # Implementation
        pass
```

---

### `static` - Cannot Be Instantiated, All Members Must Be Static

```csharp
public static class DriverFactory 
{
    // Can't do: new DriverFactory()
    // Can only call: DriverFactory.CreateDriver()
    
    public static IWebDriver CreateDriver()
    {
        // Factory method
    }
}
```

**When to use:**
- ✅ **Utility/Helper classes** with only static methods
- ✅ **Factory classes** that don't need state
- ✅ **Extension methods** container

**Rules:**
- Cannot create instance with `new`
- Cannot have instance members (all must be `static`)
- Cannot inherit from or be inherited

**Python equivalent:** Module-level functions

```python
# Python equivalent - just functions in a module
# driver_factory.py
def create_driver():
    # Factory function
    pass

# Usage: driver_factory.create_driver()
```

---

### `partial` - Class Definition Split Across Multiple Files

```csharp
// File: LoginPage.Part1.cs
public partial class LoginPage
{
    public void Login(string user, string pwd)
    {
        // Implementation
    }
}

// File: LoginPage.Part2.cs
public partial class LoginPage
{
    public void Logout()
    {
        // Implementation
    }
}

// Compiler combines both into one LoginPage class
```

**When to use:**
- ✅ **Auto-generated code** + manual code separation
- ✅ **Very large classes** (though consider refactoring instead)
- ⚠️ Rarely needed in test automation

**Python equivalent:** None

---

## Common Combinations for Selenium Framework

### 1. Singleton Pattern - `sealed` + private constructor

```csharp
public sealed class Config
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    private Config() { }  // Private constructor
}
```

**Why `sealed`?** Prevents subclass from bypassing singleton pattern  
**Why `private` constructor?** Prevents direct instantiation

---

### 2. Factory Pattern - `static` class

```csharp
public static class DriverFactory
{
    private static readonly Dictionary<BrowserType, IBrowserStrategy> Strategies = 
        new Dictionary<BrowserType, IBrowserStrategy>();
    
    public static IWebDriver CreateDriver(BrowserType browser)
    {
        // Factory logic
    }
}
```

**Why `static`?** No state needed, just utility methods  
**Can't do:** `new DriverFactory()` - compiler error

---

### 3. Base Page Pattern - `abstract` class

```csharp
public abstract class BasePage
{
    protected IWebDriver Driver;
    
    public BasePage(IWebDriver driver)
    {
        Driver = driver;
    }
    
    public abstract void Navigate();  // Subclasses must implement
    
    public BasePage Click(By locator)  // Shared implementation
    {
        Driver.FindElement(locator).Click();
        return this;
    }
}
```

**Why `abstract`?** Don't want direct instantiation of BasePage  
**Why not `sealed`?** Need subclasses (LoginPage, etc.)

---

### 4. Page Object Pattern - `public` class

```csharp
public class LoginPage : BasePage
{
    private static readonly By Username = By.Id("username");
    
    public LoginPage(IWebDriver driver) : base(driver)
    {
    }
    
    public LoginPage Login(string user, string pwd)
    {
        // Implementation
        return this;  // Fluent
    }
}
```

**Why `public`?** Tests need to access it  
**Why not `sealed`?** Might want to extend (though rare)  
**Why not `abstract`?** Need to instantiate it

---

## Quick Decision Tree

```
Need to create instances?
├─ NO → abstract or static
│   ├─ Has instance state? → abstract
│   └─ Only methods, no state? → static
│
└─ YES → public or internal
    ├─ Can be inherited?
    │   ├─ YES → public (or internal)
    │   └─ NO → sealed
    │
    └─ Visible outside assembly?
        ├─ YES → public
        └─ NO → internal
```

---

## Comparison Table: Python vs C#

| Purpose | Python | C# |
|---------|--------|-----|
| **Can't instantiate (base class)** | `ABC` + `@abstractmethod` | `abstract class` |
| **Can't inherit** | Convention only | `sealed` |
| **Utility functions** | Module-level functions | `static class` |
| **Private constructor** | `_init` convention | `private ClassName()` |
| **Force implementation** | `@abstractmethod` | `abstract` method |
| **Public class** | Default (all public) | `public class` |
| **Split class definition** | None | `partial class` |

---

## Common Interview Questions

### Q: "Why is Config class sealed?"

**Answer:**
```csharp
public sealed class Config  // sealed prevents inheritance
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    private Config() { }  // private prevents direct instantiation
}
```

> "The Config class is `sealed` to prevent inheritance that could break the singleton pattern. If someone created a subclass, they could potentially create multiple instances, violating the singleton principle. The `sealed` modifier ensures the class cannot be inherited, maintaining the guarantee of a single instance."

---

### Q: "When would you use abstract vs interface?"

**Answer:**

**Use `abstract class` when:**
- ✅ Need shared implementation (common methods)
- ✅ Have instance state/fields
- ✅ Single inheritance is okay

```csharp
public abstract class BasePage
{
    protected IWebDriver Driver;  // Shared state
    
    public BasePage Click(By locator)  // Shared implementation
    {
        Driver.FindElement(locator).Click();
        return this;
    }
}
```

**Use `interface` when:**
- ✅ Defining contracts only (no implementation)
- ✅ Need multiple inheritance
- ✅ Behavior that unrelated classes might share

```csharp
public interface IWaitStrategy
{
    IWebElement Wait(IWebDriver driver, By locator, int timeout);
    // No implementation, just contract
}
```

---

### Q: "Why use static class instead of regular class with static methods?"

**Answer:**

**`static class` (better):**
```csharp
public static class DriverFactory
{
    public static IWebDriver CreateDriver() { }
}
```

**Regular class with static methods:**
```csharp
public class DriverFactory  // Not static
{
    public static IWebDriver CreateDriver() { }
}
```
>"'static' means a class or method belongs to the class itself rather than an instance of the class. A `static class` cannot be instantiated, and all its members must be static. This is ideal for utility or factory classes where you don't need to maintain state."

> "A `static class` is better because it prevents accidental instantiation. With a regular class, someone could mistakenly do `new DriverFactory()`, which would create an unnecessary object. The `static` modifier makes the intent clear and enforces it at compile time."

---

## Practical Examples from Framework

### Singleton Config - `sealed`

```csharp
public sealed class Config  // Can't inherit
{
    private static readonly Lazy<Config> _instance = 
        new Lazy<Config>(() => new Config());
    
    public static Config Instance => _instance.Value;
    
    public string BaseUrl { get; set; }
    public int Timeout { get; set; }
    
    private Config()  // Can't instantiate
    {
        BaseUrl = "https://example.com";
        Timeout = 10;
    }
}

// Usage:
var config = Config.Instance;
string url = config.BaseUrl;
```

---

### Factory - `static`

```csharp
public static class DriverFactory  // Can't instantiate
{
    public static IWebDriver CreateDriver(BrowserType browser)
    {
        switch (browser)
        {
            case BrowserType.Chrome:
                return new ChromeDriver(new ChromeOptions());
            case BrowserType.Firefox:
                return new FirefoxDriver(new FirefoxOptions());
            default:
                throw new ArgumentException($"Unsupported: {browser}");
        }
    }
}

// Usage:
var driver = DriverFactory.CreateDriver(BrowserType.Chrome);
```

---

### Base Page - `abstract`

```csharp
public abstract class BasePage  // Can't instantiate BasePage directly
{
    protected IWebDriver Driver;
    
    public BasePage(IWebDriver driver)
    {
        Driver = driver;
    }
    
    // Abstract method - subclasses must implement
    public abstract void Navigate();
    
    // Concrete method - subclasses can use
    public BasePage Click(By locator)
    {
        Driver.FindElement(locator).Click();
        return this;
    }
}

// Can't do this:
var page = new BasePage(driver);  // Compiler error!

// Must do this:
var page = new LoginPage(driver);  // LoginPage : BasePage
```

---

### Page Object - `public`

```csharp
public class LoginPage : BasePage  // Can instantiate and inherit
{
    private static readonly By Username = By.Id("username");
    private static readonly By Password = By.Id("password");
    
    public LoginPage(IWebDriver driver) : base(driver)
    {
    }
    
    public override void Navigate()
    {
        Driver.Navigate().GoToUrl(Config.Instance.BaseUrl + "/login");
    }
    
    public LoginPage Login(string user, string pwd)
    {
        Type(Username, user);
        Type(Password, pwd);
        return this;
    }
}

// Usage:
var loginPage = new LoginPage(driver);  // OK!
loginPage.Navigate().Login("user", "pass");
```

---

## Key Takeaways for Interview

1. **`sealed`** = "Don't inherit from me" → Use for Singleton
2. **`abstract`** = "Must inherit from me" → Use for BasePage
3. **`static`** = "Can't create me" → Use for Factories/Utilities
4. **`public`** = "Everyone can see me" → Use for Page Objects
5. **`internal`** = "Only my project can see me" → Use for internal helpers

---

## Memory Aid

Think of modifiers as answering questions:

- **Can create instance?** → If no: `abstract` or `static`
- **Can inherit?** → If no: `sealed`
- **Who can see?** → `public` (everyone) or `internal` (this project)
- **Has state?** → If no: `static`, if yes: instance class

---

## Common Mistakes to Avoid

❌ **Forgetting `sealed` on Singleton**
```csharp
public class Config  // Missing sealed!
{
    private static Config _instance;
    private Config() { }
}
// Someone could inherit and break it!
```

✅ **Correct:**
```csharp
public sealed class Config  // Now safe!
```

---

❌ **Using regular class instead of static**
```csharp
public class DriverFactory  // Should be static
{
    public static IWebDriver CreateDriver() { }
}
// Can mistakenly do: new DriverFactory()
```

✅ **Correct:**
```csharp
public static class DriverFactory  // Prevents instantiation
```

---

❌ **Not marking BasePage as abstract**
```csharp
public class BasePage  // Should be abstract
{
    protected IWebDriver Driver;
    // ...
}
// Someone could do: new BasePage() - usually not intended
```

✅ **Correct:**
```csharp
public abstract class BasePage  // Forces inheritance
```

---

## Study Tips

1. **Practice identifying patterns**: When you see `sealed`, think "Singleton"
2. **Understand the why**: Don't just memorize, understand the problems each solves
3. **Compare to Python**: Relate to concepts you already know (ABC, modules, etc.)
4. **Use in interview answers**: "I'd use a `sealed` singleton for Config because..."

---

## Additional Resources

- [Microsoft Docs: Abstract Classes](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/abstract-and-sealed-classes-and-class-members)
- [Microsoft Docs: Static Classes](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/static-classes-and-static-class-members)
- [Microsoft Docs: Access Modifiers](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/access-modifiers)
