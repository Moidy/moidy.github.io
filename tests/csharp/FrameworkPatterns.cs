/*
================================================================================
Advanced Selenium Framework Patterns - C# Version

This file demonstrates advanced framework design patterns commonly discussed 
in senior-level interviews:
- Base Page class with reusable methods
- Fluent interface pattern
- Factory pattern for driver creation
- Strategy pattern for waits
- Singleton pattern for configuration
- Custom exceptions
- Page Object Model
- Element wrapper pattern

================================================================================
QUICK REFERENCE - MEMORIZATION AID
================================================================================

THE "3 AM TEST" - Will you hate yourself if this breaks at 3 AM?

PATTERN          | 3 AM NIGHTMARE                        | TECHNICAL WIN
-----------------|---------------------------------------|----------------------------------
SINGLETON        | Changing URL in 50 files             | Single source of truth
(Config)         |                                      | Thread-safe, lazy loading
                 |                                      |
FACTORY          | Adding Chrome option to 40 tests     | Encapsulated creation
(DriverFactory)  |                                      | Easy to extend
                 |                                      |
STRATEGY         | Adding new wait type = editing       | Swappable algorithms
(IWaitStrategy)  | 30 methods                           | Open/Closed principle
                 |                                      |
PAGE OBJECT      | Button ID changed, 83 files to       | DRY - change once
(BasePage)       | update                               | Test readability
                 |                                      |
FLUENT           | Tests look like random function      | Natural language flow
(return this)    | calls                                | Less verbose
                 |                                      |
WRAPPER          | StaleElementException everywhere     | Fresh references
(Element)        |                                      | Enhanced API

MEMORY TRICK: "I'm annoyed by X, so I use Y"
- Annoyed by scattered config → Singleton
- Annoyed by setup duplication → Factory  
- Annoyed by if/else wait types → Strategy
- Annoyed by duplicate locators → Page Object
- Annoyed by ugly test code → Fluent Interface
- Annoyed by stale elements → Wrapper

================================================================================
*/

using System;
using System.Collections.Generic;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Firefox;
using OpenQA.Selenium.Edge;
using OpenQA.Selenium.Support.UI;
using SeleniumExtras.WaitHelpers;
using NUnit.Framework;

namespace SeleniumFramework
{
    // ============================================================================
    // CUSTOM EXCEPTIONS - DOMAIN-SPECIFIC ERROR HANDLING
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Generic "Exception" doesn't tell you WHAT went wrong WHERE
    //   - Selenium's exceptions too broad (TimeoutException for everything)
    //   - Can't catch specific framework issues vs Selenium issues
    //
    // TECHNICAL BENEFITS:
    //   - Clarity: Exception name tells you exactly what failed
    //   - Specific Handling: catch ElementNotInteractableException vs generic
    //   - Better Debugging: Stack traces show YOUR exception names
    //   - Documentation: Exception class itself documents failure scenarios
    // ============================================================================

    public class ElementNotInteractableException : Exception
    {
        public ElementNotInteractableException(string message) : base(message) { }
    }

    public class PageNotLoadedException : Exception
    {
        public PageNotLoadedException(string message) : base(message) { }
    }

    // ============================================================================
    // CONFIGURATION MANAGEMENT - SINGLETON PATTERN
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Base URL, timeouts, and settings copy-pasted in 50+ test files
    //   - Need to change base URL? Update 50 files manually
    //   - Each test creates its own config → inconsistent settings
    //
    // TECHNICAL BENEFITS:
    //   - Single source of truth: ONE place to change config values
    //   - Memory efficient: Only one Config instance exists in memory
    //   - Thread-safe: Lazy<T> provides thread-safe initialization
    //   - Lazy initialization: Config created only when first accessed
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - Updating hardcoded URLs in 83 test files at 3 AM
    //   - Half your tests use timeout=10, half use timeout=15 (inconsistent)
    // ============================================================================

    public sealed class Config
    {
        // Thread-safe lazy initialization
        private static readonly Lazy<Config> _instance = 
            new Lazy<Config>(() => new Config());

        public static Config Instance => _instance.Value;

        public string BaseUrl { get; set; }
        public int ImplicitWait { get; set; }
        public int ExplicitWait { get; set; }
        public int PageLoadTimeout { get; set; }
        public BrowserType Browser { get; set; }
        public bool Headless { get; set; }

        // Private constructor prevents direct instantiation
        private Config()
        {
            // Default values
            BaseUrl = "https://www.selenium.dev";
            ImplicitWait = 10;
            ExplicitWait = 10;
            PageLoadTimeout = 30;
            Browser = BrowserType.Chrome;
            Headless = false;
        }

        public void LoadFromEnvironment(string environment)
        {
            // Load from config file based on environment (dev/staging/prod)
            // In real implementation, read from JSON/XML file
            switch (environment.ToLower())
            {
                case "dev":
                    BaseUrl = "https://dev.example.com";
                    break;
                case "staging":
                    BaseUrl = "https://staging.example.com";
                    break;
                case "prod":
                    BaseUrl = "https://www.example.com";
                    break;
            }
        }
    }

    // ============================================================================
    // FACTORY PATTERN + STRATEGY PATTERN - DRIVER CREATION
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Same 15 lines of Chrome setup duplicated in every test file
    //   - Boss says "add Firefox support" → copy-paste nightmare begins
    //   - Different developers set up drivers differently (inconsistent)
    //
    // TECHNICAL BENEFITS:
    //   - Encapsulation: Complex driver setup hidden in one place
    //   - Easy to extend: Add new browser by adding one strategy class
    //   - Consistent driver configuration across all tests
    //   - Strategy Pattern: Each browser has its own configuration logic
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - Need to add one Chrome option → editing 40 test files
    //   - Different environments need different driver configs
    // ============================================================================

    public enum BrowserType
    {
        Chrome,
        Firefox,
        Edge
    }

    // Strategy Pattern - Abstract browser configuration
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
            options.AddArgument("--disable-blink-features=AutomationControlled");

            if (headless)
            {
                options.AddArgument("--headless=new");
            }

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
            {
                options.AddArgument("--headless");
            }

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
            {
                options.AddArgument("--headless");
            }

            return new EdgeDriver(options);
        }
    }

    // Factory Pattern - Creates appropriate strategy and driver
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
            {
                throw new ArgumentException($"Unsupported browser: {browserType}");
            }

            var strategy = Strategies[browserType];
            var driver = strategy.CreateDriver(headless);

            // Common configuration for all browsers
            var config = Config.Instance;
            driver.Manage().Timeouts().PageLoad = TimeSpan.FromSeconds(config.PageLoadTimeout);
            driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(config.ImplicitWait);

            return driver;
        }
    }

    // ============================================================================
    // STRATEGY PATTERN - WAIT CONDITIONS
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Some elements need visibility wait, some need clickable wait
    //   - Your BasePage.FindElement() has ugly if/else blocks for wait types
    //   - Adding new wait type means editing every method that uses waits
    //
    // TECHNICAL BENEFITS:
    //   - Polymorphism: Different strategies with same interface
    //   - Swappable behavior: Change wait type without changing calling code
    //   - Easy to test: Mock different strategies independently
    //   - Adheres to Open/Closed: Add new wait types without modifying existing code
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - Need "wait for custom attribute" → rewriting FindElement() logic
    //   - if wait_type == 'clickable': elif wait_type == 'visible': elif... (code smell)
    // ============================================================================

    public interface IWaitStrategy
    {
        IWebElement Wait(IWebDriver driver, By locator, int timeout = 10);
    }

    public class PresenceWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementExists(locator));
        }
    }

    public class VisibilityWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementIsVisible(locator));
        }
    }

    public class ClickableWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementToBeClickable(locator));
        }
    }

    // ============================================================================
    // PAGE OBJECT MODEL (POM) - BASE PAGE
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Locators scattered in 100+ test files
    //   - Dev changes button ID → updating 83 test files
    //   - Same helper methods (Click, Type, Wait) duplicated everywhere
    //
    // TECHNICAL BENEFITS:
    //   - DRY: Reusable methods defined once, used everywhere
    //   - Maintainability: Change locator once, all tests updated
    //   - Readability: Tests read like business actions, not WebDriver calls
    //   - Separation of Concerns: Test logic vs page interactions separated
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - "Login button" ID changed → finding all 67 references manually
    //   - Every test has driver.FindElement(By.Id("...")).Click() → repetitive
    // ============================================================================

    public class BasePage
    {
        protected IWebDriver Driver;
        protected WebDriverWait Wait;

        public BasePage(IWebDriver driver)
        {
            Driver = driver;
            var config = Config.Instance;
            Wait = new WebDriverWait(driver, TimeSpan.FromSeconds(config.ExplicitWait));
        }

        public BasePage Open(string url)
        {
            Driver.Navigate().GoToUrl(url);
            return this;
        }

        public IWebElement FindElement(By locator, IWaitStrategy waitStrategy = null)
        {
            if (waitStrategy != null)
            {
                return waitStrategy.Wait(Driver, locator);
            }
            return Driver.FindElement(locator);
        }

        public BasePage Click(By locator, IWaitStrategy waitStrategy = null)
        {
            var strategy = waitStrategy ?? new ClickableWait();
            var element = FindElement(locator, strategy);

            try
            {
                element.Click();
            }
            catch (Exception)
            {
                // Fallback to JavaScript click
                ((IJavaScriptExecutor)Driver).ExecuteScript("arguments[0].click();", element);
            }

            return this;
        }

        public BasePage Type(By locator, string text, bool clearFirst = true)
        {
            var element = FindElement(locator, new VisibilityWait());

            if (clearFirst)
            {
                element.Clear();
            }

            element.SendKeys(text);
            return this;
        }

        public string GetText(By locator)
        {
            var element = FindElement(locator, new PresenceWait());
            return element.Text;
        }

        public string GetAttribute(By locator, string attribute)
        {
            var element = FindElement(locator, new PresenceWait());
            return element.GetAttribute(attribute);
        }

        public bool IsDisplayed(By locator)
        {
            try
            {
                var element = FindElement(locator, new PresenceWait());
                return element.Displayed;
            }
            catch (NoSuchElementException)
            {
                return false;
            }
        }

        public bool WaitForUrlContains(string text, int timeout = 10)
        {
            var wait = new WebDriverWait(Driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(d => d.Url.Contains(text));
        }

        public BasePage ScrollToElement(By locator)
        {
            var element = FindElement(locator, new PresenceWait());
            ((IJavaScriptExecutor)Driver).ExecuteScript("arguments[0].scrollIntoView(true);", element);
            return this;
        }

        public string CurrentUrl => Driver.Url;
        public string Title => Driver.Title;
    }

    // ============================================================================
    // FLUENT INTERFACE PATTERN - METHOD CHAINING
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - Test code looks like disconnected function calls
    //   - page.Navigate() then page.Search() then page.Verify() → ugly
    //   - Hard to follow the flow of actions in a test
    //
    // TECHNICAL BENEFITS:
    //   - Readability: Code reads like natural language sentences
    //   - Less verbose: Fewer variable declarations needed
    //   - Method chaining: return this from each method
    //   - Natural flow: Actions read in sequence like a story
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - Test looks like random function calls instead of user journey
    //   - Want elegant test code: page.Login().Search("item").Verify()
    // ============================================================================

    public class LoginPage : BasePage
    {
        // Locators as constants
        private static readonly By UsernameInput = By.Id("username");
        private static readonly By PasswordInput = By.Id("password");
        private static readonly By LoginButton = By.Id("login");
        private static readonly By ErrorMessage = By.CssSelector(".error-message");

        public LoginPage(IWebDriver driver) : base(driver) { }

        public LoginPage Navigate()
        {
            Open(Config.Instance.BaseUrl + "/login");
            return this;
        }

        public LoginPage EnterUsername(string username)
        {
            Type(UsernameInput, username);
            return this; // Fluent interface
        }

        public LoginPage EnterPassword(string password)
        {
            Type(PasswordInput, password);
            return this; // Fluent interface
        }

        public LoginPage ClickLogin()
        {
            Click(LoginButton);
            return this; // Fluent interface
        }

        // Complete login in one fluent chain
        public LoginPage Login(string username, string password)
        {
            return EnterUsername(username)
                .EnterPassword(password)
                .ClickLogin();
        }

        public bool IsErrorDisplayed()
        {
            return IsDisplayed(ErrorMessage);
        }
    }

    // ============================================================================
    // WRAPPER PATTERN - ELEMENT WRAPPER
    // ============================================================================
    // ANNOYING PROBLEM:
    //   - StaleElementReferenceException everywhere (element cached, page changed)
    //   - Every click needs try/catch/JavaScript fallback boilerplate
    //   - Adding behavior to WebElement requires subclassing (can't do it)
    //
    // TECHNICAL BENEFITS:
    //   - Encapsulation: Wrap IWebElement with additional behavior
    //   - Stale Reference Solution: Re-find element on each access (fresh reference)
    //   - Enhanced API: Add helper methods (Type, WaitUntilVisible, etc.)
    //   - Error Handling: Centralized handling for common issues
    //
    // WHEN YOU'LL FEEL THE PAIN:
    //   - StaleElementReferenceException in 30% of test runs
    //   - Every click has try/catch with JavaScript fallback
    // ============================================================================

    public class Element
    {
        private readonly IWebDriver _driver;
        private readonly By _locator;

        public Element(IWebDriver driver, By locator)
        {
            _driver = driver;
            _locator = locator;
        }

        // Always get fresh element to avoid stale references
        private IWebElement WebElement => _driver.FindElement(_locator);

        public Element Click(bool force = false)
        {
            try
            {
                WebElement.Click();
            }
            catch (Exception)
            {
                if (force)
                {
                    // JavaScript click fallback
                    ((IJavaScriptExecutor)_driver)
                        .ExecuteScript("arguments[0].click();", WebElement);
                }
                else
                {
                    throw;
                }
            }
            return this;
        }

        public Element Type(string text, bool clear = true)
        {
            var element = WebElement;
            if (clear)
            {
                element.Clear();
            }
            element.SendKeys(text);
            return this;
        }

        public bool IsVisible()
        {
            try
            {
                return WebElement.Displayed;
            }
            catch
            {
                return false;
            }
        }

        public Element WaitUntilVisible(int timeout = 10)
        {
            var wait = new WebDriverWait(_driver, TimeSpan.FromSeconds(timeout));
            wait.Until(ExpectedConditions.ElementIsVisible(_locator));
            return this;
        }

        public Element WaitUntilClickable(int timeout = 10)
        {
            var wait = new WebDriverWait(_driver, TimeSpan.FromSeconds(timeout));
            wait.Until(ExpectedConditions.ElementToBeClickable(_locator));
            return this;
        }

        public string Text => WebElement.Text;
        public string GetAttribute(string name) => WebElement.GetAttribute(name);
    }

    // ============================================================================
    // EXAMPLE TEST CLASS
    // ============================================================================

    [TestFixture]
    public class LoginTests
    {
        private IWebDriver _driver;

        [SetUp]
        public void Setup()
        {
            // Use Factory pattern to create driver
            var config = Config.Instance;
            _driver = DriverFactory.CreateDriver(config.Browser, config.Headless);
        }

        [Test]
        public void TestFluentLoginFlow()
        {
            // Demonstrates Fluent Interface pattern
            var loginPage = new LoginPage(_driver);
            
            loginPage
                .Navigate()
                .Login("testuser", "password123")
                .WaitForUrlContains("/dashboard");

            Assert.IsTrue(_driver.Url.Contains("/dashboard"));
        }

        [Test]
        public void TestElementWrapper()
        {
            // Demonstrates Element Wrapper pattern
            _driver.Navigate().GoToUrl("https://example.com");
            
            var username = new Element(_driver, By.Id("username"));
            var password = new Element(_driver, By.Id("password"));
            var loginBtn = new Element(_driver, By.Id("login"));

            username.WaitUntilVisible().Type("testuser");
            password.WaitUntilVisible().Type("password123");
            loginBtn.WaitUntilClickable().Click();
        }

        [TearDown]
        public void Teardown()
        {
            _driver?.Quit();
        }
    }
}
