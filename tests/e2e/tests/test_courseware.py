import pytest

from tests.e2e.conftest import LMS_BASE_URL
from tests.e2e.pages.lms.login_page import LoginPage
from tests.e2e.pages.lms.courseware_page import CoursewarePage


def test_enrolled_user_can_access_courseware(driver, seeded_course):
    login_page = LoginPage(driver, LMS_BASE_URL)
    login_page.login(seeded_course['email'], seeded_course['password'])

    courseware_page = CoursewarePage(driver, LMS_BASE_URL)
    courseware_page.navigate_to_courseware(seeded_course['course_key'])
    assert courseware_page.is_loaded()


def test_courseware_chapter_navigation(driver, seeded_course):
    login_page = LoginPage(driver, LMS_BASE_URL)
    login_page.login(seeded_course['email'], seeded_course['password'])

    courseware_page = CoursewarePage(driver, LMS_BASE_URL)
    courseware_page.navigate_to_courseware(seeded_course['course_key'])
    courseware_page.is_loaded()
    courseware_page.click_first_chapter()
    assert courseware_page.xblock_content_is_visible()
