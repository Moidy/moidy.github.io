using NUnit.Framework;
using OpenQA.Selenium;
using SeleniumFramework.Core;
using SeleniumFramework.Elements;

namespace SeleniumFramework.Tests
{
    /// <summary>
    /// Test suite demonstrating Element Wrapper pattern.
    /// Shows how wrapper prevents stale element references and provides clean API.
    /// </summary>
    [TestFixture]
    public class ElementWrapperTests
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
        [Category("Wrapper")]
        public void TestElementWrapperBasicOperations()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/login");
            var username = new Element(_driver, By.Id("username"));
            var password = new Element(_driver, By.Id("password"));

            // Act
            username.WaitUntilVisible().Type("tomsmith");
            password.WaitUntilVisible().Type("SuperSecretPassword!");

            // Assert
            Assert.AreEqual("tomsmith", username.GetAttribute("value"));
            Assert.AreEqual("SuperSecretPassword!", password.GetAttribute("value"));
        }

        [Test]
        [Category("Wrapper")]
        public void TestElementWrapperFluentInterface()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/login");
            var loginButton = new Element(_driver, By.CssSelector("button[type='submit']"));

            // Act - Demonstrates fluent chaining
            loginButton
                .WaitUntilVisible()
                .WaitUntilClickable()
                .Click();

            // Assert
            Assert.That(_driver.Url, Does.Not.Contain("/login"), 
                "Should navigate away from login page");
        }

        [Test]
        [Category("Wrapper")]
        public void TestElementVisibilityCheck()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_loading/1");
            var startButton = new Element(_driver, By.CssSelector("#start button"));
            var finishText = new Element(_driver, By.CssSelector("#finish"));

            // Act & Assert
            Assert.IsTrue(startButton.IsVisible(), "Start button should be visible");
            Assert.IsFalse(finishText.IsVisible(), "Finish text should be hidden initially");

            // Trigger loading
            startButton.Click();
            finishText.WaitUntilVisible(10);

            Assert.IsTrue(finishText.IsVisible(), "Finish text should be visible after loading");
        }

        [Test]
        [Category("Wrapper")]
        public void TestForceClickWithJavaScript()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/checkboxes");
            var checkbox = new Element(_driver, By.CssSelector("input[type='checkbox']"));

            // Act - Force click even if element might be obscured
            checkbox.Click(force: true);

            // Assert
            Assert.AreEqual("true", checkbox.GetAttribute("checked"), 
                "Checkbox should be checked after force click");
        }

        [Test]
        [Category("Wrapper")]
        public void TestScrollIntoView()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/large");
            var element = new Element(_driver, By.Id("sibling-2.1"));

            // Act
            element.ScrollIntoView().WaitUntilVisible();

            // Assert
            Assert.IsTrue(element.IsVisible(), "Element should be visible after scrolling");
        }

        [Test]
        [Category("Wrapper")]
        public void TestElementTextAndAttributes()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/login");
            var heading = new Element(_driver, By.CssSelector("h2"));
            var loginButton = new Element(_driver, By.CssSelector("button[type='submit']"));

            // Act & Assert
            Assert.That(heading.Text, Does.Contain("Login Page"));
            Assert.AreEqual("submit", loginButton.GetAttribute("type"));
        }

        [Test]
        [Category("Wrapper")]
        public void TestIsEnabledCheck()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/dynamic_controls");
            var input = new Element(_driver, By.CssSelector("#input-example input"));
            var enableButton = new Element(_driver, By.CssSelector("#input-example button"));

            // Act & Assert
            Assert.IsFalse(input.IsEnabled(), "Input should be disabled initially");

            enableButton.WaitUntilClickable().Click();
            System.Threading.Thread.Sleep(2000); // Wait for animation

            Assert.IsTrue(input.IsEnabled(), "Input should be enabled after clicking button");
        }

        [Test]
        [Category("Wrapper")]
        public void TestClearAndType()
        {
            // Arrange
            _driver.Navigate().GoToUrl("https://the-internet.herokuapp.com/login");
            var username = new Element(_driver, By.Id("username"));

            // Act
            username.Type("first_value");
            username.Clear().Type("second_value");

            // Assert
            Assert.AreEqual("second_value", username.GetAttribute("value"));
        }

        [TearDown]
        public void Teardown()
        {
            _driver?.Quit();
        }
    }
}
