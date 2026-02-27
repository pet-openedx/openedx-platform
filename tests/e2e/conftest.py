import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.student.tests.factories import AdminFactory, UserFactory
from openedx.core.djangoapps.content.course_overviews.tests.factories import CourseOverviewFactory

LMS_BASE_URL = os.environ.get('LMS_BASE_URL', 'http://localhost:8000')
CMS_BASE_URL = os.environ.get('CMS_BASE_URL', 'http://localhost:8001')
TEST_PASSWORD = 'Password1234'
E2E_USER_EMAIL = 'e2e_learner@example.com'
E2E_COURSE_KEY = os.environ.get('E2E_COURSE_KEY', 'course-v1:E2EOrg+E2ECourse+2025')


@pytest.fixture(scope='function')
def driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_driver = webdriver.Chrome(options=options)
    chrome_driver.implicitly_wait(10)
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture
def lms_user(db):
    user = UserFactory.create(is_active=True)
    yield user
    user.delete()


@pytest.fixture
def enrolled_user(db):
    course = CourseOverviewFactory.create(org='E2EOrg')
    user = UserFactory.create(is_active=True)
    enrollment = CourseEnrollment.enroll(user, course.id)
    yield user, course
    enrollment.delete()
    course.delete()
    user.delete()


@pytest.fixture(scope='session')
def seeded_course():
    return {
        'email': E2E_USER_EMAIL,
        'password': TEST_PASSWORD,
        'course_key': E2E_COURSE_KEY,
    }


@pytest.fixture
def cms_staff_user(db):
    user = AdminFactory.create(is_active=True)
    yield user
    user.delete()


@pytest.fixture
def lms_base_url():
    return LMS_BASE_URL


@pytest.fixture
def cms_base_url():
    return CMS_BASE_URL
