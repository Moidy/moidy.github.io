using NUnit.Framework;
using OpenQA.Selenium;
using SeleniumFramework.Core;
using SeleniumFramework.Elements;
using SeleniumFramework.Core.Exceptions;

namespace SeleniumFramework.Tests
{
    /// <summary>
    /// Demonstrates proper exception handling in Selenium tests.
    /// Shows when to throw ElementNotInteractableException vs other exceptions.
    /// </summary>
    [TestFixture]
    public class ExceptionTests
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
        [Category("Exceptions")]
        public void TestClickingHiddenElement_ThrowsException()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/1");
            
            // The finish text is hidden initially
            var hiddenElement = _driver.FindElement(By.CssSelector("#finish"));

            // Act & Assert - Expect exception when clicking hidden element
            Assert.Throws<ElementNotInteractableException>(() =>
            {
                if (!hiddenElement.Displayed)
                {
                    throw new ElementNotInteractableException(
                        $"Cannot interact with element: {By.CssSelector("#finish")}. Element is not visible."
                    );
                }
                hiddenElement.Click();
            });
        }

        [Test]
        [Category("Exceptions")]
        public void TestClickingDisabledButton_ThrowsException()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_controls");
            var disabledButton = _driver.FindElement(By.CssSelector("#input-example button"));
            var textInput = _driver.FindElement(By.CssSelector("#input-example input"));

            // Act & Assert - Text input is disabled initially
            Assert.Throws<ElementNotInteractableException>(() =>
            {
                if (!textInput.Enabled)
                {
                    throw new ElementNotInteractableException(
                        "Cannot type into element. Element is disabled."
                    );
                }
                textInput.SendKeys("test");
            });
        }

        [Test]
        [Category("Exceptions")]
        public void TestExceptionWithInnerException()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/1");

            // Act & Assert - Demonstrate wrapping Selenium exception
            var ex = Assert.Throws<ElementNotInteractableException>(() =>
            {
                try
                {
                    var hiddenElement = _driver.FindElement(By.CssSelector("#finish"));
                    hiddenElement.Click(); // This will throw WebDriverException
                }
                catch (WebDriverException innerEx)
                {
                    // Wrap Selenium's exception with our custom exception
                    throw new ElementNotInteractableException(
                        "Failed to interact with element on dynamic loading page",
                        innerEx
                    );
                }
            });

            // Assert - Check exception has inner exception
            Assert.IsNotNull(ex.InnerException);
            Assert.IsInstanceOf<WebDriverException>(ex.InnerException);
        }

        [Test]
        [Category("Exceptions")]
        public void TestGracefulHandling_RetryOnException()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/1");
            var startButton = _driver.FindElement(By.CssSelector("#start button"));
            var finishElement = _driver.FindElement(By.CssSelector("#finish"));

            // Start the loading process
            startButton.Click();

            // Act - Retry logic for interacting with element
            bool success = false;
            int maxRetries = 10;
            
            for (int i = 0; i < maxRetries; i++)
            {
                try
                {
                    if (!finishElement.Displayed)
                    {
                        throw new ElementNotInteractableException(
                            "Element not yet visible"
                        );
                    }
                    
                    // If we get here, element is visible
                    success = true;
                    break;
                }
                catch (ElementNotInteractableException)
                {
                    System.Threading.Thread.Sleep(500); // Wait 500ms before retry
                }
            }

            // Assert
            Assert.IsTrue(success, "Element should become visible after loading");
        }

        [Test]
        [Category("Exceptions")]
        public void TestExceptionMessage_IsDescriptive()
        {
            // Arrange
            string elementLocator = "#hidden-element";
            string expectedMessage = $"Cannot click element {elementLocator}: element is not visible";

            // Act
            var ex = new ElementNotInteractableException(expectedMessage);

            // Assert - Good exception messages help debugging at 3 AM!
            Assert.AreEqual(expectedMessage, ex.Message);
            StringAssert.Contains("not visible", ex.Message);
            StringAssert.Contains(elementLocator, ex.Message);
        }

        [TearDown]
        public void Teardown()
        {
            _driver?.Quit();
        }
    }
}
