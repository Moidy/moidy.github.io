using OpenQA.Selenium;
using SeleniumFramework.Core;

namespace SeleniumFramework.Pages
{
    /// <summary>
    /// Page Object for Login page.
    /// Demonstrates Fluent Interface pattern with method chaining.
    /// </summary>
    public class LoginPage : BasePage
    {
        // Locators as constants
        private static readonly By UsernameInput = By.Id("username");
        private static readonly By PasswordInput = By.Id("password");
        private static readonly By LoginButton = By.Id("login");
        private static readonly By ErrorMessage = By.CssSelector(".error-message");
        private static readonly By ForgotPasswordLink = By.LinkText("Forgot Password?");

        public LoginPage(IWebDriver driver) : base(driver) { }

        public LoginPage Navigate()
        {
            Open(Config.Instance.BaseUrl + "/login");
            return this;
        }

        public LoginPage EnterUsername(string username)
        {
            Type(UsernameInput, username);
            return this; // Fluent interface
        }

        public LoginPage EnterPassword(string password)
        {
            Type(PasswordInput, password);
            return this; // Fluent interface
        }

        public LoginPage ClickLogin()
        {
            Click(LoginButton);
            return this; // Fluent interface
        }

        // Complete login in one fluent chain
        public LoginPage Login(string username, string password)
        {
            return EnterUsername(username)
                .EnterPassword(password)
                .ClickLogin();
        }

        public bool IsErrorDisplayed()
        {
            return IsDisplayed(ErrorMessage);
        }

        public string GetErrorText()
        {
            return GetText(ErrorMessage);
        }

        public LoginPage ClickForgotPassword()
        {
            Click(ForgotPasswordLink);
            return this;
        }

        public bool IsOnLoginPage()
        {
            return CurrentUrl.Contains("/login");
        }
    }
}
