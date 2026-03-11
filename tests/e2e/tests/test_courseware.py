from settings import LMS_BASE_URL
from pages.lms.login_page import LoginPage
from pages.lms.courseware_page import CoursewarePage


def test_enrolled_user_can_access_courseware(page, seeded_course):
    LoginPage(page, LMS_BASE_URL).login(seeded_course['email'], seeded_course['password'])

    courseware_page = CoursewarePage(page, LMS_BASE_URL)
    courseware_page.navigate_to_courseware(seeded_course['course_key'])
    courseware_page.is_loaded()


def test_courseware_chapter_navigation(page, seeded_course):
    LoginPage(page, LMS_BASE_URL).login(seeded_course['email'], seeded_course['password'])

    courseware_page = CoursewarePage(page, LMS_BASE_URL)
    courseware_page.navigate_to_courseware(seeded_course['course_key'])
    courseware_page.is_loaded()
    courseware_page.click_first_chapter()
    courseware_page.xblock_content_is_visible()
