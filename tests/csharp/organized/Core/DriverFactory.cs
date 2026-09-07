using System;
using System.Collections.Generic;
using OpenQA.Selenium;
using SeleniumFramework.Strategies.Browser;

namespace SeleniumFramework.Core
{
    /// <summary>
    /// Factory for creating WebDriver instances with proper configuration.
    /// Uses Strategy pattern to handle different browser types.
    /// </summary>
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

        public static IWebDriver CreateDriver()
        {
            var config = Config.Instance;
            return CreateDriver(config.Browser, config.Headless);
        }
    }
}
