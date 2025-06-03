
from django.db import models
from django.db.models import Count, Sum, Case, When, Value, FloatField, F
from .models import Attendance
from users.models import User

def get_user_attendance_summary(user_id, start_date, end_date):
    """
    Get attendance summary for a specific user between dates
    """
    queryset = Attendance.objects.filter(
        user_id=user_id,
        date__range=[start_date, end_date]
    ).aggregate(
        total_days=Count('id'),
        present_days=Sum(Case(When(status='present', then=1), default=0, output_field=models.IntegerField())),
        absent_days=Sum(Case(When(status='absent', then=1), default=0, output_field=models.IntegerField())),
        late_days=Sum(Case(When(status='late', then=1), default=0, output_field=models.IntegerField())),
        leave_days=Sum(Case(When(status='leave', then=1), default=0, output_field=models.IntegerField())),
        half_days=Sum(Case(When(status='halfday', then=1), default=0, output_field=models.IntegerField())),
        work_hours=Sum('work_hours', default=0)
    )
    
    # Get user information
    try:
        user = User.objects.get(id=user_id)
        queryset['user_name'] = user.first_name + " " + user.last_name
        queryset['user_id'] = user_id
    except User.DoesNotExist:
        queryset['user_name'] = "Unknown"
        queryset['user_id'] = user_id
        
    # Calculate attendance percentage
    total_days = queryset['total_days'] or 0
    present_days = queryset['present_days'] or 0
    
    if total_days > 0:
        queryset['attendance_percentage'] = (present_days / total_days) * 100
    else:
        queryset['attendance_percentage'] = 0.0
        
    # Convert None values to 0
    for key in queryset:
        if queryset[key] is None:
            queryset[key] = 0
    
    return queryset

def get_attendance_summary(start_date, end_date):
    """
    Get attendance summary for all users between dates
    """
    # Using Django ORM
    summary = User.objects.annotate(
        total_work_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date]
        )),
        present_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date],
            attendance__status='present'
        )),
        absent_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date],
            attendance__status='absent'
        )),
        late_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date],
            attendance__status='late'
        )),
        leave_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date],
            attendance__status='leave'
        )),
        half_days=Count('attendance', filter=models.Q(
            attendance__date__range=[start_date, end_date],
            attendance__status='halfday'
        )),
        work_hours=Sum('attendance__work_hours', filter=models.Q(
            attendance__date__range=[start_date, end_date]
        ), default=0),
        attendance_percentage=Case(
            When(total_work_days=0, then=Value(0.0)),
            default=100.0 * F('present_days') / F('total_work_days'),
            output_field=FloatField()
        )
    ).order_by('last_name', 'first_name')
    
    return summary