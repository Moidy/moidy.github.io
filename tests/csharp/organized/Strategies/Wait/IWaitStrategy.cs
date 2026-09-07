using OpenQA.Selenium;

namespace SeleniumFramework.Strategies.Wait
{
    /// <summary>
    /// Strategy interface for different wait conditions.
    /// Allows swapping wait behavior without changing calling code.
    /// </summary>
    public interface IWaitStrategy
    {
        IWebElement Wait(IWebDriver driver, By locator, int timeout = 10);
    }
}
