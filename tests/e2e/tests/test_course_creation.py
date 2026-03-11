from uuid import uuid4

from settings import LMS_BASE_URL, CMS_BASE_URL, TEST_PASSWORD
from pages.cms.cms_login_page import CmsLoginPage
from pages.cms.cms_home_page import CmsHomePage
from pages.cms.course_outline_page import CourseOutlinePage


def test_staff_can_create_course(page, cms_staff_user):
    CmsLoginPage(page, LMS_BASE_URL, CMS_BASE_URL).login(cms_staff_user.email, TEST_PASSWORD)

    home_page = CmsHomePage(page, CMS_BASE_URL)
    home_page.is_loaded()
    home_page.create_course(name="Test E2E Course", org="E2EOrg", number="E2ENum", run=uuid4().hex[:8])

    assert "/course/" in page.url


def test_created_course_outline_loads(page, cms_staff_user):
    CmsLoginPage(page, LMS_BASE_URL, CMS_BASE_URL).login(cms_staff_user.email, TEST_PASSWORD)

    home_page = CmsHomePage(page, CMS_BASE_URL)
    home_page.is_loaded()
    home_page.create_course(name="Test E2E Outline Course", org="E2EOrg", number="E2EOutline", run=uuid4().hex[:8])

    outline_page = CourseOutlinePage(page, CMS_BASE_URL)
    outline_page.is_loaded()
    assert outline_page.get_current_course_key() is not None
