from selenium.webdriver.common.by import By

from tests.e2e.pages.base_page import BasePage


class CoursewarePage(BasePage):
    def navigate_to_courseware(self, course_key):
        self.navigate_to(f'/courses/{course_key}/courseware/')

    def is_loaded(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.course-index')

    def get_chapter_links(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '.chapter a')

    def click_first_chapter(self):
        chapters = self.get_chapter_links()
        if chapters:
            chapters[0].click()

    def xblock_content_is_visible(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.xblock-student_view')
