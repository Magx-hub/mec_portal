# attendance/models.py
from django.db import models
from datetime import datetime, timedelta
from users.models import User

class ATTENDANCE_STATUSES(models.TextChoices):
    PRESENT = 'present'
    LATE = 'late'
    ABSENT = 'absent'
    LEAVE = 'leave'
    HALFDAY = 'halfday'

class Attendance(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    date = models.DateField()
    week_num = models.IntegerField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUSES.choices, default=ATTENDANCE_STATUSES.PRESENT)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teacher.user.first_name} {self.teacher.user.last_name}'s attendance on {self.date}"
    
    def save(self, *args, **kwargs):
        if self.check_in_time and self.check_out_time:
            check_in = datetime.combine(self.date, self.check_in_time)
            check_out = datetime.combine(self.date, self.check_out_time)
            self.work_hours = round((check_out - check_in).total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

