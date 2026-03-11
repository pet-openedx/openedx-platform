from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def is_loaded(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.dashboard-main')

    def get_course_titles(self):
        return [el.text for el in self.driver.find_elements(By.CSS_SELECTOR, '.course-title')]

    def has_course(self, course_display_name):
        titles = self.get_course_titles()
        return any(course_display_name in title for title in titles)
