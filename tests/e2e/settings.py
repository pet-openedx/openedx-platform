import os

LMS_BASE_URL = os.environ.get("LMS_BASE_URL", "http://localhost:8000")
CMS_BASE_URL = os.environ.get("CMS_BASE_URL", "http://localhost:8001")
TEST_PASSWORD = "Password1234"
E2E_USER_EMAIL = "e2e_learner@example.com"
E2E_COURSE_KEY = os.environ.get("E2E_COURSE_KEY", "course-v1:E2EOrg+E2ECourse+2025")
