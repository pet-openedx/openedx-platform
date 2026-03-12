from pages.base_page import BasePage


class CourseOutlinePage(BasePage):
    def is_loaded(self):
        self.page.wait_for_url('**/course/**')

    def get_current_course_key(self):
        parts = self.page.url.split('/course/')
        if len(parts) > 1:
            return parts[1].strip('/')
        return None
