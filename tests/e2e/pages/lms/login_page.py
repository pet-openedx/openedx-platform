from pages.base_page import BasePage


class LoginPage(BasePage):
    def login(self, email, password):
        self.navigate_to('/login')
        self.page.locator('#login-email').fill(email)
        self.page.locator('#login-password').fill(password)
        self.page.locator('button.js-login').click()
        self.page.wait_for_url('**/dashboard**')
