from selenium.webdriver.common.by import By

from tests.e2e.pages.base_page import BasePage


class CourseAboutPage(BasePage):
    def navigate_to_course_about(self, course_id):
        self.navigate_to(f'/courses/{course_id}/about')

    def is_loaded(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.course-about')

    def enroll(self):
        self.wait_for_element_clickable(By.CSS_SELECTOR, '.register-button').click()
        self.wait_for_url_contains('/dashboard')
