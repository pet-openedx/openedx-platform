from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def navigate_to(self, path):
        self.driver.get(self.base_url + path)

    def wait_for_element(self, by, locator, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )

    def wait_for_element_clickable(self, by, locator, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )

    def wait_for_url_contains(self, fragment, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(fragment)
        )
