from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lessonplans.models import LessonPlan
from attendance.models import Attendance
from users.models import User

class Command(BaseCommand):
    help = 'Set up user groups and permissions'

    def handle(self, *args, **kwargs):
        teacher_group, _ = Group.objects.get_or_create(name='Teachers')
        headmaster_group, _ = Group.objects.get_or_create(name='Headmasters')

        lessonplan_ct = ContentType.objects.get_for_model(LessonPlan)
        attendance_ct = ContentType.objects.get_for_model(Attendance)
        user_ct = ContentType.objects.get_for_model(User)

        teacher_perms = [
            Permission.objects.get(codename='add_lessonplan'),
            Permission.objects.get(codename='change_lessonplan'),
            Permission.objects.get(codename='delete_lessonplan'),
            Permission.objects.get(codename='view_lessonplan'),
            Permission.objects.get(codename='view_attendance'),
        ]
        teacher_group.permissions.set(teacher_perms)

        headmaster_perms = Permission.objects.filter(
            content_type__in=[lessonplan_ct, attendance_ct, user_ct]
        )
        headmaster_group.permissions.set(headmaster_perms)

        self.stdout.write(self.style.SUCCESS('Groups and permissions set up successfully.'))