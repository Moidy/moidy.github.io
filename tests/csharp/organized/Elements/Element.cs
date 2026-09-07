using System;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumExtras.WaitHelpers;

namespace SeleniumFramework.Elements
{
    /// <summary>
    /// Wrapper class for IWebElement that prevents stale element references.
    /// Always fetches fresh element on each operation.
    /// </summary>
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

        public Element Clear()
        {
            WebElement.Clear();
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

        public bool IsEnabled()
        {
            try
            {
                return WebElement.Enabled;
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

        public Element ScrollIntoView()
        {
            ((IJavaScriptExecutor)_driver)
                .ExecuteScript("arguments[0].scrollIntoView(true);", WebElement);
            return this;
        }

        public string Text => WebElement.Text;
        public string GetAttribute(string name) => WebElement.GetAttribute(name);
    }
}
