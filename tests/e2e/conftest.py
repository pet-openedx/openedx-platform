import base64
import html
import os
from uuid import uuid4

import pytest

from seed.mongo_seeder import get_client
from seed.mysql_seeder import (
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
from settings import CMS_BASE_URL, E2E_COURSE_KEY, E2E_USER_EMAIL, LMS_BASE_URL, TEST_PASSWORD


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


@pytest.fixture
def page(page):
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(15000)
    page._e2e_listeners_registered = False
    page._e2e_nav_urls = []
    page._e2e_network = []
    page._e2e_console = []
    yield page


@pytest.fixture(autouse=True)
def server_logs(request):
    lms_start = _file_end_pos('/tmp/lms.log')
    cms_start = _file_end_pos('/tmp/cms.log')
    yield
    request.node._e2e_lms_log = _read_log_slice('/tmp/lms.log', lms_start)
    request.node._e2e_cms_log = _read_log_slice('/tmp/cms.log', cms_start)


@pytest.fixture(autouse=True)
def attach_page_to_node(request, page):
    request.node._e2e_page = page
    yield


def _file_end_pos(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def _read_log_slice(path, start_pos):
    try:
        with open(path, 'r', errors='replace') as f:
            f.seek(start_pos)
            return f.read()
    except OSError:
        return ''


def _html_nav_section(urls):
    if not urls:
        return ''
    items = ''.join(f'<li>{html.escape(u)}</li>' for u in urls)
    return (
        '<details><summary><strong>Navigation URLs</strong></summary>'
        f'<ul>{items}</ul></details>'
    )


def _html_network_table(records):
    if not records:
        return ''
    rows = []
    for r in records:
        status = r.get('status') or ''
        color = ' style="color:red"' if isinstance(status, int) and status >= 400 else ''
        rows.append(
            f'<tr{color}>'
            f'<td>{html.escape(r.get("method",""))}</td>'
            f'<td>{html.escape(r.get("url",""))}</td>'
            f'<td>{status}</td>'
            f'<td>{r.get("elapsed_ms","")}</td>'
            f'</tr>'
        )
    body = ''.join(rows)
    return (
        '<details><summary><strong>Network Requests</strong></summary>'
        '<table><thead><tr><th>Method</th><th>URL</th><th>Status</th><th>ms</th></tr></thead>'
        f'<tbody>{body}</tbody></table></details>'
    )


def _html_console_table(records):
    if not records:
        return ''
    rows = []
    for r in records:
        color = ' style="color:red"' if r.get('type') == 'error' else ''
        rows.append(
            f'<tr{color}>'
            f'<td>{html.escape(r.get("type",""))}</td>'
            f'<td>{html.escape(r.get("text",""))}</td>'
            f'</tr>'
        )
    body = ''.join(rows)
    return (
        '<details><summary><strong>Browser Console</strong></summary>'
        '<table><thead><tr><th>Type</th><th>Message</th></tr></thead>'
        f'<tbody>{body}</tbody></table></details>'
    )


def _html_log_block(label, text):
    return (
        f'<details><summary><strong>{html.escape(label)}</strong></summary>'
        f'<pre>{html.escape(text)}</pre></details>'
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != 'call':
        return
    from pytest_html import extras as html_extras
    extra = getattr(report, 'extras', [])
    page = getattr(item, '_e2e_page', None)
    if page:
        extra.append(html_extras.html(_html_nav_section(page._e2e_nav_urls)))
        extra.append(html_extras.html(_html_network_table(page._e2e_network)))
        extra.append(html_extras.html(_html_console_table(page._e2e_console)))
        if report.failed:
            screenshot_b64 = base64.b64encode(page.screenshot(type='png')).decode('utf-8')
            extra.append(html_extras.png(screenshot_b64))
    lms_log = getattr(item, '_e2e_lms_log', '').strip()
    cms_log = getattr(item, '_e2e_cms_log', '').strip()
    if lms_log:
        extra.append(html_extras.html(_html_log_block('LMS Server Logs', lms_log)))
    if cms_log:
        extra.append(html_extras.html(_html_log_block('CMS Server Logs', cms_log)))
    report.extras = extra
