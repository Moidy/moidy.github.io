using NUnit.Framework;
using SeleniumFramework.Core;

namespace SeleniumFramework.Tests
{
    /// <summary>
    /// Test suite for Config Singleton pattern.
    /// Demonstrates configuration management and singleton behavior.
    /// </summary>
    [TestFixture]
    public class ConfigTests
    {
        [Test]
        [Category("Unit")]
        public void TestConfigIsSingleton()
        {
            // Arrange & Act
            var config1 = Config.Instance;
            var config2 = Config.Instance;

            // Assert
            Assert.AreSame(config1, config2, 
                "Both references should point to the same instance");
        }

        [Test]
        [Category("Unit")]
        public void TestConfigHasDefaultValues()
        {
            // Arrange
            var config = Config.Instance;

            // Assert
            Assert.IsNotNull(config.BaseUrl);
            Assert.IsTrue(config.ImplicitWait > 0);
            Assert.IsTrue(config.ExplicitWait > 0);
            Assert.IsTrue(config.PageLoadTimeout > 0);
        }

        [Test]
        [Category("Unit")]
        public void TestLoadEnvironmentConfig()
        {
            // Arrange
            var config = Config.Instance;

            // Act
            config.LoadFromEnvironment("dev");

            // Assert
            Assert.That(config.BaseUrl, Does.Contain("dev"), 
                "Dev environment should have 'dev' in URL");

            // Act
            config.LoadFromEnvironment("staging");

            // Assert
            Assert.That(config.BaseUrl, Does.Contain("staging"), 
                "Staging environment should have 'staging' in URL");
        }

        [Test]
        [Category("Unit")]
        public void TestConfigCanBeModified()
        {
            // Arrange
            var config = Config.Instance;
            string originalUrl = config.BaseUrl;

            // Act
            config.BaseUrl = "https://custom.example.com";

            // Assert
            Assert.AreEqual("https://custom.example.com", config.BaseUrl);

            // Cleanup - restore original
            config.BaseUrl = originalUrl;
        }

        [Test]
        [Category("Unit")]
        public void TestBrowserTypeConfiguration()
        {
            // Arrange
            var config = Config.Instance;

            // Act
            config.Browser = BrowserType.Firefox;

            // Assert
            Assert.AreEqual(BrowserType.Firefox, config.Browser);

            // Act
            config.Browser = BrowserType.Chrome;

            // Assert
            Assert.AreEqual(BrowserType.Chrome, config.Browser);
        }

        [Test]
        [Category("Unit")]
        public void TestHeadlessModeConfiguration()
        {
            // Arrange
            var config = Config.Instance;

            // Act
            config.Headless = true;

            // Assert
            Assert.IsTrue(config.Headless);

            // Cleanup
            config.Headless = false;
        }
    }
}
