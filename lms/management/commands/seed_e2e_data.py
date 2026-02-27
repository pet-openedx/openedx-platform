from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from common.djangoapps.student.models import CourseEnrollment

E2E_USER_EMAIL = 'e2e_learner@example.com'
E2E_USER_PASSWORD = 'Password1234'
E2E_COURSE_ORG = 'E2EOrg'
E2E_COURSE_NUMBER = 'E2ECourse'
E2E_COURSE_RUN = '2025'

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed E2E test data: a known user, course, and enrollment'

    def handle(self, *args, **options):
        from xmodule.modulestore.django import modulestore
        from xmodule.modulestore.tests.factories import CourseFactory, BlockFactory
        from opaque_keys.edx.keys import CourseKey

        course_key = CourseKey.from_string(
            f'course-v1:{E2E_COURSE_ORG}+{E2E_COURSE_NUMBER}+{E2E_COURSE_RUN}'
        )

        store = modulestore()
        existing = store.get_course(course_key)
        if not existing:
            course = CourseFactory.create(
                org=E2E_COURSE_ORG,
                number=E2E_COURSE_NUMBER,
                run=E2E_COURSE_RUN,
                display_name='E2E Test Course',
            )
            chapter = BlockFactory.create(
                parent=course,
                category='chapter',
                display_name='Chapter 1',
            )
            sequential = BlockFactory.create(
                parent=chapter,
                category='sequential',
                display_name='Lesson 1',
            )
            BlockFactory.create(
                parent=sequential,
                category='vertical',
                display_name='Unit 1',
            )
        else:
            course = existing

        user, created = User.objects.get_or_create(
            email=E2E_USER_EMAIL,
            defaults={'username': 'e2e_learner', 'is_active': True},
        )
        if created:
            user.set_password(E2E_USER_PASSWORD)
            user.save()

        CourseEnrollment.enroll(user, course.id if hasattr(course, 'id') else course_key)

        self.stdout.write(f'Seeded E2E data. Course key: {course_key}')
