from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def driver_factory(driver_name):

    @staticmethod
    def get_driver():
        if driver_name == "chrome":
            return _create_Chrome_Driver()
        elif driver_name == "firefox":
            return webdriver.Firefox()
        elif driver_name == "edge":
            return webdriver.Edge()
        else:
            raise ValueError(f"Unsupported driver: {driver_name}")

    def _create_Chrome_Driver():
        """Create Chrome driver with options"""
        opts = webdriver.ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        
        headless = Config().headless
        if headless:
            opts.add_argument("--headless=new")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        
        config = Config()
        driver.set_page_load_timeout(config.page_load_timeout)
        driver.implicitly_wait(config.implicit_wait)
        
        return driver

    def 