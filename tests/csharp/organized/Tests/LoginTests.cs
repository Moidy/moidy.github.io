using NUnit.Framework;
using OpenQA.Selenium;
using SeleniumFramework.Core;
using SeleniumFramework.Pages;

namespace SeleniumFramework.Tests
{
    /// <summary>
    /// Test suite demonstrating Login functionality using the framework.
    /// Shows Fluent Interface pattern and Page Object Model usage.
    /// </summary>
    [TestFixture]
    public class LoginTests
    {
        private IWebDriver _driver;
        private LoginPage _loginPage;

        [SetUp]
        public void Setup()
        {
            // Configure before creating driver
            var config = Config.Instance;
            config.BaseUrl = "https://www.saucedemo.com";
            config.Browser = BrowserType.Chrome;
            config.Headless = false;

            // Use Factory pattern to create driver
            _driver = DriverFactory.CreateDriver();
            _loginPage = new LoginPage(_driver);
        }

        [Test]
        [Category("Smoke")]
        public void TestSuccessfulLogin()
        {
            // Arrange
            string username = "standard_user";
            string password = "secret_sauce";

            // Act - Demonstrates fluent interface
            _loginPage
                .Navigate()
                .Login(username, password);

            // Assert
            Assert.IsTrue(_driver.Url.Contains("inventory.html"), 
                "Should navigate to inventory page after successful login");
        }

        [Test]
        [Category("Negative")]
        public void TestLoginWithInvalidCredentials()
        {
            // Arrange
            string invalidUsername = "invalid_user";
            string invalidPassword = "wrong_password";

            // Act
            _loginPage
                .Navigate()
                .Login(invalidUsername, invalidPassword);

            // Assert
            Assert.IsTrue(_loginPage.IsErrorDisplayed(), 
                "Error message should be displayed for invalid credentials");
        }

        [Test]
        [Category("Smoke")]
        public void TestLoginWithEmptyFields()
        {
            // Act
            _loginPage
                .Navigate()
                .ClickLogin();

            // Assert
            Assert.IsTrue(_loginPage.IsErrorDisplayed(), 
                "Error message should be displayed when fields are empty");
            Assert.IsTrue(_loginPage.IsOnLoginPage(), 
                "Should remain on login page");
        }

        [Test]
        [Category("UI")]
        public void TestFluentMethodChaining()
        {
            // Demonstrates clean fluent interface
            _loginPage
                .Navigate()
                .EnterUsername("test_user")
                .EnterPassword("test_pass")
                .ClickLogin();

            // This reads like natural language - that's the point!
        }

        [Test]
        [Category("Negative")]
        public void TestLockedOutUser()
        {
            // Arrange
            string lockedUser = "locked_out_user";
            string password = "secret_sauce";

            // Act
            _loginPage
                .Navigate()
                .Login(lockedUser, password);

            // Assert
            Assert.IsTrue(_loginPage.IsErrorDisplayed());
            string errorText = _loginPage.GetErrorText();
            Assert.That(errorText, Does.Contain("locked out"), 
                "Error should indicate user is locked out");
        }

        [TearDown]
        public void Teardown()
        {
            _driver?.Quit();
        }
    }
}
