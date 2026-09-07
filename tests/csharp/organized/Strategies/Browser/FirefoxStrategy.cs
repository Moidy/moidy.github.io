using OpenQA.Selenium;
using OpenQA.Selenium.Firefox;

namespace SeleniumFramework.Strategies.Browser
{
    /// <summary>
    /// Firefox browser configuration strategy.
    /// Handles Firefox-specific options and capabilities.
    /// </summary>
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
}
