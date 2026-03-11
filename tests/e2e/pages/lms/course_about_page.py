from pages.base_page import BasePage


class CourseAboutPage(BasePage):
    def navigate_to_course_about(self, course_id):
        self.navigate_to(f'/courses/{course_id}/about')

    def is_loaded(self):
        self.page.locator('.course-info').wait_for()

    def enroll(self):
        self.page.locator('a.register').click()
        self.page.wait_for_url('**/dashboard**')
