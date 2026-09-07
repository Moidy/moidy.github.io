using NUnit.Framework;
using OpenQA.Selenium;
using SeleniumFramework.Core;
using SeleniumFramework.Strategies.Wait;

namespace SeleniumFramework.Tests
{
    /// <summary>
    /// Test suite demonstrating Strategy pattern usage for waits.
    /// Shows how to swap wait strategies without changing test code.
    /// </summary>
    [TestFixture]
    public class StrategyTests
    {
        private IWebDriver _driver;

        [SetUp]
        public void Setup()
        {
            var config = Config.Instance;
            config.BaseUrl = "https://the-internet.herokuapp.com";
            config.Headless = false;
            
            _driver = DriverFactory.CreateDriver(BrowserType.Chrome);
        }

        [Test]
        [Category("Strategy")]
        public void TestPresenceWaitStrategy()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/2");
            var strategy = new PresenceWait();
            var startButton = By.CssSelector("#start button");

            // Act
            var element = strategy.Wait(_driver, startButton, 5);

            // Assert
            Assert.IsNotNull(element, "Element should be found using PresenceWait");
        }

        [Test]
        [Category("Strategy")]
        public void TestVisibilityWaitStrategy()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/1");
            var strategy = new VisibilityWait();
            var startButton = By.CssSelector("#start button");

            // Act
            startButton.Click(); // Trigger the dynamic loading
            var finishLocator = By.CssSelector("#finish h4");
            var element = strategy.Wait(_driver, finishLocator, 10);

            // Assert
            Assert.IsNotNull(element, "Element should be visible using VisibilityWait");
            Assert.IsTrue(element.Displayed, "Element should be displayed");
        }

        [Test]
        [Category("Strategy")]
        public void TestClickableWaitStrategy()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_controls");
            var strategy = new ClickableWait();
            var enableButton = By.CssSelector("#input-example button");

            // Act
            var element = strategy.Wait(_driver, enableButton, 5);

            // Assert
            Assert.IsNotNull(element, "Element should be clickable using ClickableWait");
            Assert.IsTrue(element.Enabled, "Element should be enabled");
        }

        [Test]
        [Category("Strategy")]
        public void TestSwappingStrategies()
        {
            // This test demonstrates how easy it is to swap strategies
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/login");
            var usernameLocator = By.Id("username");

            // Act - Use different strategies for same element
            IWaitStrategy presenceStrategy = new PresenceWait();
            IWaitStrategy visibilityStrategy = new VisibilityWait();
            IWaitStrategy clickableStrategy = new ClickableWait();

            var element1 = presenceStrategy.Wait(_driver, usernameLocator);
            var element2 = visibilityStrategy.Wait(_driver, usernameLocator);
            var element3 = clickableStrategy.Wait(_driver, usernameLocator);

            // Assert - All should work because element is present, visible, and clickable
            Assert.IsNotNull(element1);
            Assert.IsNotNull(element2);
            Assert.IsNotNull(element3);
        }

        [Test]
        [Category("Strategy")]
        public void TestStrategyWithDynamicContent()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/2");
            var startButton = By.CssSelector("#start button");
            var finishText = By.CssSelector("#finish h4");

            // Act
            new ClickableWait().Wait(_driver, startButton).Click();
            var result = new VisibilityWait().Wait(_driver, finishText, 10);

            // Assert
            Assert.That(result.Text, Does.Contain("Hello World!"), 
                "Should see the dynamic content after waiting");
        }

        [TearDown]
        public void Teardown()
        {
            _driver?.Quit();
        }
    }
}
