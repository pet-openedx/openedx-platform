import os
from datetime import datetime

import pymongo
from bson import ObjectId

_DEFAULT_MONGO_URL = "mongodb://localhost:27017"
_DEFAULT_MONGO_DB = "openedx"
_SYSTEM_USER_ID = 1


def get_client(mongo_url=None):
    return pymongo.MongoClient(mongo_url or os.environ.get("E2E_MONGO_URL", _DEFAULT_MONGO_URL))


def _db(client):
    return client[os.environ.get("E2E_MONGO_DB", _DEFAULT_MONGO_DB)]


def seed_course(client, org, course_num, run, display_name="E2E Test Course"):
    db = _db(client)
    active_versions = db["modulestore.active_versions"]

    if active_versions.find_one({"org": org, "course": course_num, "run": run}):
        return

    now = datetime.utcnow()
    course_def_id = ObjectId()
    chapter_def_id = ObjectId()
    seq_def_id = ObjectId()
    vertical_def_id = ObjectId()
    struct_id = ObjectId()

    def_edit = {
        "edited_on": now,
        "edited_by": _SYSTEM_USER_ID,
        "previous_version": None,
        "source_version": None,
    }

    db["modulestore.definitions"].insert_many([
        {
            "_id": course_def_id,
            "block_type": "course",
            "fields": {},
            "defaults": {},
            "edit_info": {**def_edit, "original_version": course_def_id},
            "schema_version": 1,
        },
        {
            "_id": chapter_def_id,
            "block_type": "chapter",
            "fields": {},
            "defaults": {},
            "edit_info": {**def_edit, "original_version": chapter_def_id},
            "schema_version": 1,
        },
        {
            "_id": seq_def_id,
            "block_type": "sequential",
            "fields": {},
            "defaults": {},
            "edit_info": {**def_edit, "original_version": seq_def_id},
            "schema_version": 1,
        },
        {
            "_id": vertical_def_id,
            "block_type": "vertical",
            "fields": {},
            "defaults": {},
            "edit_info": {**def_edit, "original_version": vertical_def_id},
            "schema_version": 1,
        },
    ])

    block_edit = {
        "edited_on": now,
        "edited_by": _SYSTEM_USER_ID,
        "update_version": struct_id,
        "previous_version": None,
        "source_version": None,
    }

    db["modulestore.structures"].insert_one({
        "_id": struct_id,
        "root": ["course", "course"],
        "blocks": {
            "course": {
                "block_type": "course",
                "definition": course_def_id,
                "fields": {
                    "display_name": display_name,
                    "children": [["chapter", "e2e_chapter"]],
                },
                "defaults": {},
                "edit_info": block_edit,
            },
            "e2e_chapter": {
                "block_type": "chapter",
                "definition": chapter_def_id,
                "fields": {
                    "display_name": "Chapter 1",
                    "children": [["sequential", "e2e_sequential"]],
                },
                "defaults": {},
                "edit_info": block_edit,
            },
            "e2e_sequential": {
                "block_type": "sequential",
                "definition": seq_def_id,
                "fields": {
                    "display_name": "Lesson 1",
                    "children": [["vertical", "e2e_vertical"]],
                },
                "defaults": {},
                "edit_info": block_edit,
            },
            "e2e_vertical": {
                "block_type": "vertical",
                "definition": vertical_def_id,
                "fields": {
                    "display_name": "Unit 1",
                    "children": [],
                },
                "defaults": {},
                "edit_info": block_edit,
            },
        },
        "previous_version": None,
        "original_version": struct_id,
        "schema_version": 1,
        "edit_info": {
            "edited_on": now,
            "edited_by": _SYSTEM_USER_ID,
            "previous_version": None,
        },
    })

    active_versions.insert_one({
        "org": org,
        "course": course_num,
        "run": run,
        "versions": {
            "published-branch": struct_id,
            "draft-branch": struct_id,
        },
        "last_update": now,
        "search_targets": {},
        "schema_version": 1,
    })


def delete_course(client, org, course_num, run):
    db = _db(client)
    active_versions = db["modulestore.active_versions"]

    entry = active_versions.find_one({"org": org, "course": course_num, "run": run})
    if not entry:
        return

    struct_ids = list(entry.get("versions", {}).values())

    def_ids = []
    for struct_doc in db["modulestore.structures"].find({"_id": {"$in": struct_ids}}):
        def_ids.extend(block["definition"] for block in struct_doc.get("blocks", {}).values())

    db["modulestore.structures"].delete_many({"_id": {"$in": struct_ids}})
    db["modulestore.definitions"].delete_many({"_id": {"$in": def_ids}})
    active_versions.delete_one({"org": org, "course": course_num, "run": run})
