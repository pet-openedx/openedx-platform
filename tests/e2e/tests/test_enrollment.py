from tests.e2e.conftest import LMS_BASE_URL, TEST_PASSWORD
from tests.e2e.pages.lms.course_about_page import CourseAboutPage
from tests.e2e.pages.lms.dashboard_page import DashboardPage
from tests.e2e.pages.lms.login_page import LoginPage


def test_user_sees_enrolled_course_on_dashboard(driver, enrolled_user):
    user, course = enrolled_user
    login_page = LoginPage(driver, LMS_BASE_URL)
    login_page.login(user.email, TEST_PASSWORD)

    dashboard_page = DashboardPage(driver, LMS_BASE_URL)
    dashboard_page.is_loaded()
    assert dashboard_page.has_course(course.display_name)


def test_user_can_enroll_via_course_about_page(driver, lms_user, course_factory):
    course = course_factory(org="E2EOrg", display_name="E2E Enrollment Test Course", enrollment_start=None, enrollment_end=None)

    login_page = LoginPage(driver, LMS_BASE_URL)
    login_page.login(lms_user.email, TEST_PASSWORD)

    about_page = CourseAboutPage(driver, LMS_BASE_URL)
    about_page.navigate_to_course_about(str(course.id))
    about_page.is_loaded()
    about_page.enroll()

    dashboard_page = DashboardPage(driver, LMS_BASE_URL)
    dashboard_page.is_loaded()
    assert dashboard_page.has_course(course.display_name)
