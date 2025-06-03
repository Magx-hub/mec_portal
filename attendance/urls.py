# attendance/urls.py
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Main Attendance CRUD views
    path('', views.AttendanceListView.as_view(), name='attendance-list'),
    path('create/', views.AttendanceCreateView.as_view(), name='attendance-create'),
    path('update/<int:pk>/', views.AttendanceUpdateView.as_view(), name='attendance-update'),
    path('delete/<int:pk>/', views.AttendanceDeleteView.as_view(), name='attendance-delete'),
    
    # Teacher-specific views
    path('my-attendance/', views.TeacherAttendanceView.as_view(), name='teacher-attendance'),
    
    # Reports and Analytics
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/summary/', views.AttendanceSummaryView.as_view(), name='attendance-summary'),
    path('reports/user/<int:user_id>/', views.UserAttendanceSummaryView.as_view(), name='user-attendance-summary'),
    path('reports/export-pdf/', views.ExportAttendancePDFView.as_view(), name='export-pdf'),
    
    # Dashboard view
    path('dashboard/', views.AttendanceDashboardView.as_view(), name='dashboard'),
    
    # Bulk operations
    path('bulk-create/', views.BulkAttendanceCreateView.as_view(), name='bulk-create'),
]

