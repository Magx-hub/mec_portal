# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('headmaster', 'Headmaster'),
        ('teacher', 'Teacher'),
    )

    DEPARTMENT_CHOICES = (
        ('preschool', 'PreSchool'),
        ('lower_primary', 'Lower Primary'),
        ('upper_primary', 'Upper Primary'),
        ('jhs', 'Junior High School'),
        ('management', 'Management')
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='teacher'
    )
    
    # Add the missing department field
    department = models.CharField(
        max_length=50, 
        # blank=True, 
        # null=True,
        choices=DEPARTMENT_CHOICES,
        default='lower_primary',
    )

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
