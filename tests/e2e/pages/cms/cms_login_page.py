from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CmsLoginPage(BasePage):
    def __init__(self, driver, lms_base_url, cms_base_url):
        super().__init__(driver, lms_base_url)
        self.cms_base_url = cms_base_url

    def login(self, email, password):
        self.navigate_to('/login')
        self.wait_for_element(By.ID, 'login-email').send_keys(email)
        self.driver.find_element(By.ID, 'login-password').send_keys(password)
        self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-action="login"]').click()
        self.wait_for_url_contains('/dashboard')
        self.driver.get(self.cms_base_url + '/home')
        self.wait_for_url_contains('/home')
