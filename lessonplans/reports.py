# reports.py
from django.db.models import Count, Q
from django.utils import timezone
from .models import LessonPlan, LessonPlanCheck

def generate_presentation_report(start_date=None, end_date=None):
    """
    Generate report of presented lesson plans with statistics
    """
    if not start_date:
        start_date = timezone.now() - timezone.timedelta(days=30)
    if not end_date:
        end_date = timezone.now()
    
    # Basic statistics
    total_presented = LessonPlanCheck.objects.filter(
        status='presented',
        date_checked__date__range=(start_date, end_date)
    ).count()
    
    # By subject breakdown
    by_subject = (
        LessonPlanCheck.objects
        .filter(status='presented', date_checked__date__range=(start_date, end_date))
        .values('lesson_plan__subject')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # By grade_level breakdown
    by_garde_level = (
        LessonPlanCheck.objects
        .filter(status='presented', date_checked__date__range=(start_date, end_date))
        .values('lesson_plan__grade_level')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # By teacher breakdown
    by_teacher = (
        LessonPlanCheck.objects
        .filter(status='presented', date_checked__date__range=(start_date, end_date))
        .values('lesson_plan__created_by__username')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    return {
        'period': {'start': start_date, 'end': end_date},
        'total_presented': total_presented,
        'by_subject': list(by_subject),
        'by_grade_level': list(by_garde_level),
        'by_teacher': list(by_teacher),
    }