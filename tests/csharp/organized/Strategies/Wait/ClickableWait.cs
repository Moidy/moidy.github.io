using System;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumExtras.WaitHelpers;

namespace SeleniumFramework.Strategies.Wait
{
    /// <summary>
    /// Waits for element to be clickable (visible and enabled).
    /// Use for buttons, links, and any interactive elements.
    /// </summary>
    public class ClickableWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementToBeClickable(locator));
        }
    }
}
