from tests.e2e.seed.mongo_seeder import get_client, seed_course
from tests.e2e.seed.mysql_seeder import get_engine, seed_from_yaml

E2E_COURSE_ORG = "E2EOrg"
E2E_COURSE_NUM = "E2ECourse"
E2E_COURSE_RUN = "2025"
E2E_COURSE_DISPLAY_NAME = "E2E Test Course"


def main():
    engine = get_engine()
    seed_from_yaml(engine)
    print("MySQL: seeded users, course overview, enrollment from base.yml")

    client = get_client()
    seed_course(client, E2E_COURSE_ORG, E2E_COURSE_NUM, E2E_COURSE_RUN, E2E_COURSE_DISPLAY_NAME)
    print(f"MongoDB: seeded course course-v1:{E2E_COURSE_ORG}+{E2E_COURSE_NUM}+{E2E_COURSE_RUN}")

    client.close()
    engine.dispose()


if __name__ == "__main__":
    main()
