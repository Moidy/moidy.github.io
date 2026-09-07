using System;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumExtras.WaitHelpers;

namespace SeleniumFramework.Strategies.Wait
{
    /// <summary>
    /// Waits for element to be visible (displayed and height/width > 0).
    /// Use for elements that need to be visible before interaction.
    /// </summary>
    public class VisibilityWait : IWaitStrategy
    {
        public IWebElement Wait(IWebDriver driver, By locator, int timeout = 10)
        {
            var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(timeout));
            return wait.Until(ExpectedConditions.ElementIsVisible(locator));
        }
    }
}
