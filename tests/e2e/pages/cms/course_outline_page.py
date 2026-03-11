from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CourseOutlinePage(BasePage):
    def is_loaded(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.wrapper-mast')

    def get_current_course_key(self):
        url = self.driver.current_url
        parts = url.split('/course/')
        if len(parts) > 1:
            return parts[1].strip('/')
        return None
