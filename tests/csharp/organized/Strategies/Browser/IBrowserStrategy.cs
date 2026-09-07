using OpenQA.Selenium;

namespace SeleniumFramework.Strategies.Browser
{
    /// <summary>
    /// Strategy interface for creating browser-specific WebDriver instances.
    /// Allows adding new browsers without modifying existing code.
    /// </summary>
    public interface IBrowserStrategy
    {
        IWebDriver CreateDriver(bool headless);
    }
}
