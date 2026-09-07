using System;

namespace SeleniumFramework.Core
{
    /// <summary>
    /// Singleton configuration manager for the test framework.
    /// Thread-safe using Lazy<T> initialization.
    /// </summary>
    public sealed class Config
    {
        // Thread-safe lazy initialization
        private static readonly Lazy<Config> _instance = 
            new Lazy<Config>(() => new Config());

        public static Config Instance => _instance.Value;

        public string BaseUrl { get; set; }
        public int ImplicitWait { get; set; }
        public int ExplicitWait { get; set; }
        public int PageLoadTimeout { get; set; }
        public BrowserType Browser { get; set; }
        public bool Headless { get; set; }

        // Private constructor prevents direct instantiation
        private Config()
        {
            // Default values
            BaseUrl = "https://www.selenium.dev";
            ImplicitWait = 10;
            ExplicitWait = 10;
            PageLoadTimeout = 30;
            Browser = BrowserType.Chrome;
            Headless = false;
        }

        public void LoadFromEnvironment(string environment)
        {
            // Load from config file based on environment (dev/staging/prod)
            // In real implementation, read from JSON/XML file
            switch (environment.ToLower())
            {
                case "dev":
                    BaseUrl = "https://dev.example.com";
                    break;
                case "staging":
                    BaseUrl = "https://staging.example.com";
                    break;
                case "prod":
                    BaseUrl = "https://www.example.com";
                    break;
            }
        }
    }

    public enum BrowserType
    {
        Chrome,
        Firefox,
        Edge
    }
}
