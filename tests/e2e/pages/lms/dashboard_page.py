from pages.base_page import BasePage


class DashboardPage(BasePage):
    def is_loaded(self):
        self.page.locator('#dashboard-main').wait_for()

    def has_course(self, course_display_name):
        titles = self.page.locator('.course-title').all_text_contents()
        return any(course_display_name in title for title in titles)
