using System;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using SeleniumFramework.Core;
using SeleniumFramework.Strategies.Wait;

namespace SeleniumFramework.Pages
{
    /// <summary>
    /// Base class for all Page Objects.
    /// Provides common functionality like navigation, element finding, and interactions.
    /// </summary>
    public abstract class BasePage
    {
        protected IWebDriver Driver;
        protected WebDriverWait Wait;

        protected BasePage(IWebDriver driver)
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
}
