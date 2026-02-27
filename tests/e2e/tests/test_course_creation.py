import pytest
from uuid import uuid4

from tests.e2e.conftest import LMS_BASE_URL, CMS_BASE_URL, TEST_PASSWORD
from tests.e2e.pages.cms.cms_login_page import CmsLoginPage
from tests.e2e.pages.cms.cms_home_page import CmsHomePage
from tests.e2e.pages.cms.course_outline_page import CourseOutlinePage


@pytest.mark.django_db(transaction=True)
def test_staff_can_create_course(driver, cms_staff_user):
    cms_login_page = CmsLoginPage(driver, LMS_BASE_URL, CMS_BASE_URL)
    cms_login_page.login(cms_staff_user.email, TEST_PASSWORD)

    home_page = CmsHomePage(driver, CMS_BASE_URL)
    home_page.is_loaded()

    run = uuid4().hex[:8]
    home_page.create_course(
        name='Test E2E Course',
        org='E2EOrg',
        number='E2ENum',
        run=run,
    )

    assert '/course/' in driver.current_url


@pytest.mark.django_db(transaction=True)
def test_created_course_outline_loads(driver, cms_staff_user):
    cms_login_page = CmsLoginPage(driver, LMS_BASE_URL, CMS_BASE_URL)
    cms_login_page.login(cms_staff_user.email, TEST_PASSWORD)

    home_page = CmsHomePage(driver, CMS_BASE_URL)
    home_page.is_loaded()

    run = uuid4().hex[:8]
    home_page.create_course(
        name='Test E2E Outline Course',
        org='E2EOrg',
        number='E2EOutline',
        run=run,
    )

    outline_page = CourseOutlinePage(driver, CMS_BASE_URL)
    assert outline_page.is_loaded()
    assert outline_page.get_current_course_key() is not None
