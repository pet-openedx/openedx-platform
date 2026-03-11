from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    def login(self, email, password):
        self.navigate_to('/login')
        self.wait_for_element(By.ID, 'login-email').send_keys(email)
        self.driver.find_element(By.ID, 'login-password').send_keys(password)
        self.wait_for_element_clickable(By.CSS_SELECTOR, 'button[data-action="login"]').click()
        self.wait_for_url_contains('/dashboard')
