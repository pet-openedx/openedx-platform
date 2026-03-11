from pages.base_page import BasePage


class CmsHomePage(BasePage):
    def is_loaded(self):
        self.page.locator('.new-course-button').wait_for()

    def create_course(self, name, org, number, run):
        self.page.locator('.new-course-button').click()
        self.page.locator('#new-course-name').fill(name)
        self.page.locator('#new-course-org').fill(org)
        self.page.locator('#new-course-number').fill(number)
        self.page.locator('#new-course-run').fill(run)
        self.page.locator('.new-course-save').click()
        self.page.wait_for_url('**/course/**')
