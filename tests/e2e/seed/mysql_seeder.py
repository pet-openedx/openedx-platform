import base64
import hashlib
import os
import secrets
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import yaml
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.dialects.mysql import insert as mysql_insert

_DEFAULT_DB_URL = "mysql+pymysql://openedx:VMGPqaWL@localhost:3306/openedx"

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def make_password(plaintext, iterations=260000):
    salt = secrets.token_hex(8)
    dk = hashlib.pbkdf2_hmac("sha256", plaintext.encode("utf-8"), salt.encode("utf-8"), iterations)
    b64 = base64.b64encode(dk).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt}${b64}"


def get_engine(db_url=None):
    return create_engine(db_url or os.environ.get("E2E_DB_URL", _DEFAULT_DB_URL))


def _table(engine, name):
    meta = MetaData()
    return Table(name, meta, autoload_with=engine)


def insert_user(engine, username, email, password, is_staff=False, is_superuser=False):
    table = _table(engine, "auth_user")
    row = {
        "username": username,
        "email": email,
        "password": make_password(password),
        "first_name": "",
        "last_name": "",
        "is_superuser": is_superuser,
        "is_staff": is_staff,
        "is_active": True,
        "date_joined": datetime.utcnow(),
        "last_login": None,
    }
    with engine.begin() as conn:
        conn.execute(mysql_insert(table).values(**row).on_duplicate_key_update(is_active=True))
        return conn.execute(
            text("SELECT id FROM auth_user WHERE username = :u"), {"u": username}
        ).scalar()


def insert_userprofile(engine, user_id, name=""):
    table = _table(engine, "auth_userprofile")
    row = {
        "user_id": user_id,
        "name": name,
        "meta": "{}",
        "courseware": "course.xml",
        "language": "",
        "location": "",
    }
    with engine.begin() as conn:
        conn.execute(mysql_insert(table).values(**row).on_duplicate_key_update(name=name))


def insert_course_overview(engine, course_id, org, display_name, **kwargs):
    table = _table(engine, "course_overviews_courseoverview")
    parts = course_id.replace("course-v1:", "").split("+")
    course_num = parts[1] if len(parts) > 1 else ""
    location = f"block-v1:{'+'.join(parts)}+type@course+block@course"
    now = datetime.utcnow()
    row = {
        "id": course_id,
        "version": 0,
        "created": now,
        "modified": now,
        "org": org,
        "display_name": display_name,
        "display_number_with_default": kwargs.get("display_number_with_default", course_num),
        "display_org_with_default": kwargs.get("display_org_with_default", org),
        "_location": location,
        "_pre_requisite_courses_json": "[]",
        "course_image_url": "",
        "banner_image_url": "",
        "invitation_only": kwargs.get("invitation_only", False),
        "self_paced": kwargs.get("self_paced", False),
        "mobile_available": kwargs.get("mobile_available", False),
        "visible_to_staff_only": kwargs.get("visible_to_staff_only", False),
        "has_highlights": kwargs.get("has_highlights", False),
        "certificates_display_behavior": kwargs.get("certificates_display_behavior", "end"),
        "certificates_show_before_end": kwargs.get("certificates_show_before_end", False),
        "cert_html_view_enabled": kwargs.get("cert_html_view_enabled", False),
        "has_any_active_web_certificate": kwargs.get("has_any_active_web_certificate", False),
        "cert_name_short": kwargs.get("cert_name_short", ""),
        "cert_name_long": kwargs.get("cert_name_long", ""),
        "catalog_visibility": kwargs.get("catalog_visibility", "both"),
        "language": kwargs.get("language", ""),
        "eligible_for_financial_aid": kwargs.get("eligible_for_financial_aid", False),
        "allow_proctoring_opt_out": kwargs.get("allow_proctoring_opt_out", False),
        "enable_proctored_exams": kwargs.get("enable_proctored_exams", False),
        "entrance_exam_enabled": kwargs.get("entrance_exam_enabled", False),
        "entrance_exam_id": kwargs.get("entrance_exam_id", ""),
        "entrance_exam_minimum_score_pct": kwargs.get("entrance_exam_minimum_score_pct", 0.0),
        "force_on_flexible_peer_openassessments": kwargs.get("force_on_flexible_peer_openassessments", False),
        "start": kwargs.get("start", None),
        "end": kwargs.get("end", None),
        "enrollment_start": kwargs.get("enrollment_start"),
        "enrollment_end": kwargs.get("enrollment_end"),
    }
    with engine.begin() as conn:
        conn.execute(
            mysql_insert(table).values(**row).on_duplicate_key_update(
                display_name=display_name, modified=now
            )
        )


def insert_enrollment(engine, user_id, course_id, mode="audit"):
    table = _table(engine, "student_courseenrollment")
    row = {
        "user_id": user_id,
        "course_id": course_id,
        "is_active": True,
        "mode": mode,
        "created": datetime.utcnow(),
    }
    with engine.begin() as conn:
        conn.execute(mysql_insert(table).values(**row).on_duplicate_key_update(is_active=True))


def delete_user(engine, user_id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM student_courseenrollment WHERE user_id = :id"), {"id": user_id})
        conn.execute(text("DELETE FROM auth_userprofile WHERE user_id = :id"), {"id": user_id})
        conn.execute(text("DELETE FROM auth_user WHERE id = :id"), {"id": user_id})


def delete_course_overview(engine, course_id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM student_courseenrollment WHERE course_id = :id"), {"id": course_id})
        conn.execute(text("DELETE FROM course_overviews_courseoverview WHERE id = :id"), {"id": course_id})


def make_user(user_id, username, email, password):
    return SimpleNamespace(id=user_id, username=username, email=email, password=password)


def make_course(course_id, display_name):
    return SimpleNamespace(id=course_id, display_name=display_name)


def seed_from_yaml(engine, fixture_name="base"):
    with open(FIXTURES_DIR / f"{fixture_name}.yml") as f:
        data = yaml.safe_load(f)

    auth_user_table = _table(engine, "auth_user")
    auth_profile_table = _table(engine, "auth_userprofile")
    overview_table = _table(engine, "course_overviews_courseoverview")
    enrollment_table = _table(engine, "student_courseenrollment")
    now = datetime.utcnow()

    with engine.begin() as conn:
        for row in data.get("auth_user", []):
            row = dict(row)
            row["password"] = make_password(row.pop("password"))
            conn.execute(
                mysql_insert(auth_user_table).values(**row).on_duplicate_key_update(is_active=row["is_active"])
            )

        user_ids = {
            row["username"]: conn.execute(
                text("SELECT id FROM auth_user WHERE username = :u"), {"u": row["username"]}
            ).scalar()
            for row in data.get("auth_user", [])
        }

        for row in data.get("auth_userprofile", []):
            row = dict(row)
            row["user_id"] = user_ids[row.pop("user_ref")]
            conn.execute(
                mysql_insert(auth_profile_table).values(**row).on_duplicate_key_update(name=row["name"])
            )

        for row in data.get("course_overviews_courseoverview", []):
            row = dict(row)
            row.setdefault("created", now)
            row.setdefault("modified", now)
            conn.execute(
                mysql_insert(overview_table).values(**row).on_duplicate_key_update(
                    display_name=row["display_name"], modified=now
                )
            )

        for row in data.get("student_courseenrollment", []):
            row = dict(row)
            row["user_id"] = user_ids[row.pop("user_ref")]
            conn.execute(
                mysql_insert(enrollment_table).values(**row).on_duplicate_key_update(is_active=row["is_active"])
            )
