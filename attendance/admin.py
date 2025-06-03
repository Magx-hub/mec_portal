from django.contrib import admin
from .models import Attendance



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'check_in_time', 'check_out_time', 'work_hours')
    list_filter = ('date', 'status')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'teacher__department')
    date_hierarchy = 'date'
    #autocomplete_fields = ['teacher']
