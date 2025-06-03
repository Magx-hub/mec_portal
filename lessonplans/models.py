# lessonplans/models.py
from django.db import models
from django.urls import reverse
from users.models import User

class LessonPlan(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=50)
    date_of_lesson = models.DateField()
    duration = models.IntegerField(help_text="Duration in minutes")
    lesson_number = models.IntegerField()  # Fixed typo: was IntehgerField
    week_number = models.IntegerField()
    strand = models.CharField(max_length=200)
    sub_strand = models.CharField(max_length=200)
    content_standard = models.TextField()
    indicator = models.TextField()
    performance_indicator = models.CharField(max_length=200)
    core_competencies = models.TextField()
    key_words = models.CharField(max_length=200)
    starter = models.TextField()
    starter_resources = models.TextField()
    main = models.TextField()
    main_resources = models.TextField()
    plenary = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject} (Grade {self.grade_level})"

    def get_absolute_url(self):
        return reverse('lessonplans:lesson_detail', kwargs={'pk': self.pk})

    # Add method to check ownership
    def is_owner(self, user):
        return self.created_by == user

    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = "Lesson Plans"




class LessonPlanCheck(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('checked', 'Checked'),
        ('presented', 'Presented'),
        ('rejected', 'Rejected'),
    ]
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_checked = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)


    def __str__(self):
        return f"{self.lesson_plan.title} - {self.get_status_display()} by {self.checked_by.username}"

    class Meta:
        ordering = ['-date_checked']
        verbose_name_plural = "Lesson Plan Checks"
        unique_together = ['lesson_plan', 'checked_by']  # Prevent duplicate checks



    def mark_as_checked(self, user, status='checked', notes=None):
        """
        Method to mark a lesson plan as checked/presented by headmaster
        """
        if not user.user_type == 'headmaster':
            raise ValueError("Only headmasters can check lesson plans")
            
        check, created = LessonPlanCheck.objects.update_or_create(
            lesson_plan=self,
            checked_by=user,
            defaults={
                'status': status,
                'notes': notes
            }
        )
        return check
    

    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.lessonplancheck_set.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
    

    def display_rating(self):
        avg = self.average_rating
        return f"{avg:.1f}/5" if avg else "Not rated"
    display_rating.short_description = 'Rating'