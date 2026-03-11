from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CmsHomePage(BasePage):
    def is_loaded(self):
        return self.wait_for_element(By.CSS_SELECTOR, '.new-course-button')

    def create_course(self, name, org, number, run):
        self.wait_for_element_clickable(By.CSS_SELECTOR, '.new-course-button').click()
        self.wait_for_element(By.ID, 'new-course-name').send_keys(name)
        self.driver.find_element(By.ID, 'new-course-org').send_keys(org)
        self.driver.find_element(By.ID, 'new-course-number').send_keys(number)
        self.driver.find_element(By.ID, 'new-course-run').send_keys(run)
        self.wait_for_element_clickable(By.CSS_SELECTOR, '.new-course-save').click()
        self.wait_for_url_contains('/course/')
