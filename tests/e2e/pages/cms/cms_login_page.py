from pages.base_page import BasePage


class CmsLoginPage(BasePage):
    def __init__(self, page, lms_base_url, cms_base_url):
        super().__init__(page, lms_base_url)
        self.cms_base_url = cms_base_url

    def login(self, email, password):
        self.page.route(
            lambda url: "localhost:2001" in url,
            lambda route: route.fulfill(status=200, content_type="text/html", body="<html><body></body></html>")
        )
        self.page.goto(self.cms_base_url + '/home')
        self.page.locator('#login-email').fill(email)
        self.page.locator('#login-password').fill(password)
        self.page.locator('button.js-login').click()
        self.page.wait_for_url('**/home**')
