using OpenQA.Selenium;
using OpenQA.Selenium.Edge;

namespace SeleniumFramework.Strategies.Browser
{
    /// <summary>
    /// Edge browser configuration strategy.
    /// Handles Edge-specific options and capabilities.
    /// </summary>
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
}
