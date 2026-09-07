using System;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumExtras.WaitHelpers;

namespace SeleniumFramework.Strategies.Wait
{
    /// <summary>
    /// Waits for element to exist in DOM (may not be visible).
    /// Use when you need to check element presence regardless of visibility.
    /// </summary>
    public class PresenceWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementExists(locator));
        }
    }
}
