using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;

namespace SeleniumFramework.Strategies.Browser
{
    /// <summary>
    /// Chrome browser configuration strategy.
    /// Handles Chrome-specific options and capabilities.
    /// </summary>
    public class ChromeStrategy : IBrowserStrategy
    {
        public IWebDriver CreateDriver(bool headless)
        {
            var options = new ChromeOptions();
            options.AddArgument("--no-sandbox");
            options.AddArgument("--disable-dev-shm-usage");
            options.AddArgument("--window-size=1920,1080");
            options.AddArgument("--disable-blink-features=AutomationControlled");

            if (headless)
            {
                options.AddArgument("--headless=new");
            }

            return new ChromeDriver(options);
        }
    }
}
