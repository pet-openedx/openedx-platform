from pages.base_page import BasePage


class CoursewarePage(BasePage):
    def navigate_to_courseware(self, course_key):
        self.navigate_to(f'/courses/{course_key}/courseware/')

    def is_loaded(self):
        self.page.locator('#course-content').wait_for()

    def click_first_chapter(self):
        self.page.locator('a.chapter').first.click()

    def xblock_content_is_visible(self):
        self.page.locator('.xblock-student_view').wait_for()
