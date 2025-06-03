# urls.py
from django.urls import path
from . import views

app_name = 'lessonplans'

urlpatterns = [
    path('', views.LessonPlanListView.as_view(), name='lesson_list'),
    path('lesson/<int:pk>/', views.LessonPlanDetailView.as_view(), name='lesson_detail'),
    path('lesson/new/', views.LessonPlanWizard.as_view(), name='lesson_create_wizard'),
    path('lesson/<int:pk>/edit/', views.LessonPlanUpdateView.as_view(), name='lesson_edit'),
    path('lesson/<int:pk>/delete/', views.LessonPlanDeleteView.as_view(), name='lesson_delete'),
    path('lesson/<int:pk>/export_pdf/', views.export_lessonplan_pdf, name='lessonplan_export_pdf'),
    path('lesson/<int:pk>/check/', views.check_lesson_plan, name='lesson_check'),
    path('report/status_pdf/', views.export_all_lessonplans_status_pdf, name='lessonplan_status_report_pdf'),
]
