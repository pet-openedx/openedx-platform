import os
from uuid import uuid4

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.e2e.seed.mongo_seeder import get_client
from tests.e2e.seed.mysql_seeder import (
    delete_course_overview,
    delete_user,
    get_engine,
    insert_course_overview,
    insert_enrollment,
    insert_user,
    insert_userprofile,
    make_course,
    make_user,
)

LMS_BASE_URL = os.environ.get("LMS_BASE_URL", "http://localhost:8000")
CMS_BASE_URL = os.environ.get("CMS_BASE_URL", "http://localhost:8001")
TEST_PASSWORD = "Password1234"
E2E_USER_EMAIL = "e2e_learner@example.com"
E2E_COURSE_KEY = os.environ.get("E2E_COURSE_KEY", "course-v1:E2EOrg+E2ECourse+2025")


@pytest.fixture(scope="session")
def db_engine():
    engine = get_engine()
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def mongo_client():
    client = get_client()
    yield client
    client.close()


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chrome_driver = webdriver.Chrome(options=options)
    chrome_driver.implicitly_wait(10)
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture
def lms_user(db_engine):
    suffix = uuid4().hex[:8]
    username = f"testuser_{suffix}"
    email = f"{username}@test.com"
    user_id = insert_user(db_engine, username=username, email=email, password=TEST_PASSWORD)
    insert_userprofile(db_engine, user_id)
    yield make_user(user_id, username, email, TEST_PASSWORD)
    delete_user(db_engine, user_id)


@pytest.fixture
def enrolled_user(db_engine):
    suffix = uuid4().hex[:8]
    username = f"enrolled_{suffix}"
    email = f"{username}@test.com"
    course_id = f"course-v1:E2EOrg+E2EEnroll{suffix}+2025"
    display_name = f"E2E Enrolled Course {suffix}"

    user_id = insert_user(db_engine, username=username, email=email, password=TEST_PASSWORD)
    insert_userprofile(db_engine, user_id)
    insert_course_overview(db_engine, course_id, org="E2EOrg", display_name=display_name)
    insert_enrollment(db_engine, user_id, course_id)

    yield make_user(user_id, username, email, TEST_PASSWORD), make_course(course_id, display_name)

    delete_user(db_engine, user_id)
    delete_course_overview(db_engine, course_id)


@pytest.fixture
def cms_staff_user(db_engine):
    suffix = uuid4().hex[:8]
    username = f"staffuser_{suffix}"
    email = f"{username}@test.com"
    user_id = insert_user(db_engine, username=username, email=email, password=TEST_PASSWORD, is_staff=True, is_superuser=True)
    insert_userprofile(db_engine, user_id)
    yield make_user(user_id, username, email, TEST_PASSWORD)
    delete_user(db_engine, user_id)


@pytest.fixture
def course_factory(db_engine):
    created = []

    def factory(org, display_name, **kwargs):
        suffix = uuid4().hex[:8]
        course_id = f"course-v1:{org}+E2E{suffix}+2025"
        insert_course_overview(db_engine, course_id, org=org, display_name=display_name, **kwargs)
        course = make_course(course_id, display_name)
        created.append(course_id)
        return course

    yield factory

    for course_id in created:
        delete_course_overview(db_engine, course_id)


@pytest.fixture(scope="session")
def seeded_course():
    return {
        "email": E2E_USER_EMAIL,
        "password": TEST_PASSWORD,
        "course_key": E2E_COURSE_KEY,
    }


@pytest.fixture
def lms_base_url():
    return LMS_BASE_URL


@pytest.fixture
def cms_base_url():
    return CMS_BASE_URL
