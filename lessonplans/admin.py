
# admin.py
from django.contrib import admin
from .models import LessonPlan

@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'grade_level', 'lesson_number', 'week_number', 'created_by', 'date_created']
    list_filter = ['subject', 'grade_level', 'strand', 'created_by', 'date_created']
    search_fields = ['title', 'subject', 'key_words', 'content_standard']
    readonly_fields = ['date_created', 'date_modified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subject', 'grade_level', 'date_of_lesson', 'duration')
        }),
        ('Lesson Structure', {
            'fields': ('lesson_number', 'week_number', 'strand', 'sub_strand')
        }),
        ('Standards & Competencies', {
            'fields': ('content_standard', 'indicator', 'performance_indicator', 'core_competencies', 'key_words')
        }),
        ('Lesson Content', {
            'fields': ('starter', 'starter_resources', 'main', 'main_resources', 'plenary')
        }),
        ('Metadata', {
            'fields': ('created_by', 'date_created', 'date_modified'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)