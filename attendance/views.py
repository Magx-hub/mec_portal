# attendance/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import datetime, timedelta
import json
import weasyprint

from users.decorators import headmaster_required, teacher_required
from users.mixins import OwnershipRequiredMixin
from .models import Attendance
from users.models import User
from .utils import get_attendance_summary, get_user_attendance_summary


# ---- Attendance Views ----
class AttendanceListView(LoginRequiredMixin, OwnershipRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 10
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters if provided
        teacher_id = self.request.GET.get('teacher')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        status = self.request.GET.get('status')
        
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
            
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass filter parameters to the template
        context['selected_teacher'] = self.request.GET.get('teacher', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['selected_status'] = self.request.GET.get('status', '')
        
        # Get all teachers for the dropdown
        context['teachers'] = User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
        
        # Get status choices for filter dropdown
        from .models import ATTENDANCE_STATUSES
        context['status_choices'] = ATTENDANCE_STATUSES.choices
        
        return context


@method_decorator(headmaster_required, name='dispatch')
class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    fields = ['teacher', 'date', 'week_num', 'status', 'check_in_time', 'check_out_time', 'remarks']
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
        context['form_title'] = 'Create Attendance Record'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Attendance record created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@method_decorator(headmaster_required, name='dispatch')
class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    fields = ['teacher', 'date', 'week_num', 'status', 'check_in_time', 'check_out_time', 'remarks']
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
        context['form_title'] = 'Update Attendance Record'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Attendance record updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@method_decorator(headmaster_required, name='dispatch')
class AttendanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:attendance-list')
    context_object_name = 'attendance'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Attendance record deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---- Teacher Self-Service Views ----
@method_decorator(teacher_required, name='dispatch')
class TeacherAttendanceView(LoginRequiredMixin, ListView):
    """View for teachers to see their own attendance records"""
    model = Attendance
    template_name = 'attendance/teacher_attendance.html'
    context_object_name = 'attendances'
    paginate_by = 15
    ordering = ['-date']
    
    def get_queryset(self):
        # Teachers can only see their own records
        queryset = Attendance.objects.filter(teacher=self.request.user)
        
        # Apply date filters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
            
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Calculate summary statistics for the teacher
        queryset = self.get_queryset()
        context['total_records'] = queryset.count()
        context['present_days'] = queryset.filter(status='present').count()
        context['absent_days'] = queryset.filter(status='absent').count()
        context['late_days'] = queryset.filter(status='late').count()
        context['leave_days'] = queryset.filter(status='leave').count()
        
        return context


# ---- Reports Views ----
@method_decorator(headmaster_required, name='dispatch')
class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
        
        # Default dates (current month)
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        context['start_date'] = first_day_of_month.strftime('%Y-%m-%d')
        context['end_date'] = today.strftime('%Y-%m-%d')
        
        return context


class UserAttendanceSummaryView(LoginRequiredMixin, View):
    """Get attendance summary for a specific user"""
    
    def get(self, request, user_id):
        # Verify user exists and is a teacher
        teacher = get_object_or_404(User, id=user_id, user_type='teacher')
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({
                'error': 'Invalid date format. Use YYYY-MM-DD.'
            }, status=400)
        
        # Validate date range
        if start_date > end_date:
            return JsonResponse({
                'error': 'Start date cannot be after end date.'
            }, status=400)
        
        try:
            summary = get_user_attendance_summary(user_id, start_date, end_date)
            return JsonResponse(summary)
        except Exception as e:
            return JsonResponse({
                'error': f'Error generating summary: {str(e)}'
            }, status=500)


class AttendanceSummaryView(LoginRequiredMixin, View):
    """Get attendance summary for all teachers or filtered results"""
    
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Set default dates if none provided (last 30 days)
        if not start_date or not end_date:
            today = datetime.now().date()
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

        # Parse and validate dates
        try:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            error_msg = 'Invalid date format. Use YYYY-MM-DD format.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            else:
                messages.error(request, error_msg)
                return render(request, 'attendance/reports.html')
        
        # Validate date range
        if parsed_start > parsed_end:
            error_msg = 'Start date cannot be after end date.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=400)
            else:
                messages.error(request, error_msg)
                return render(request, 'attendance/reports.html')
        
        try:
            summary = get_attendance_summary(parsed_start, parsed_end)
            
            # Convert queryset to list of dicts with proper error handling
            summary_data = []
            
            # Initialize totals
            total_present = total_absent = total_late = total_leave = total_hours = 0
            attendance_percentages = []
            
            for user in summary:
                present = getattr(user, 'present_days', 0) or 0
                absent = getattr(user, 'absent_days', 0) or 0
                late = getattr(user, 'late_days', 0) or 0
                leave = getattr(user, 'leave_days', 0) or 0
                hours = float(getattr(user, 'work_hours', 0) or 0)
                attendance_pct = float(getattr(user, 'attendance_percentage', 0) or 0)
                
                # Accumulate totals
                total_present += present
                total_absent += absent
                total_late += late
                total_leave += leave
                total_hours += hours
                attendance_percentages.append(attendance_pct)
                
                try:
                    summary_data.append({
                        'user_id': getattr(user, 'id', 0),
                        'user_name': f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
                        'department': getattr(user, 'department', ''),
                        'total_work_days': getattr(user, 'total_work_days', 0),
                        'present_days': present,
                        'absent_days': absent,
                        'late_days': late,
                        'leave_days': leave,
                        'half_days': getattr(user, 'half_days', 0),
                        'work_hours': hours,
                        'attendance_percentage': round(attendance_pct, 2),
                    })
                except Exception as e:
                    # Log the error but continue processing other users
                    print(f"Error processing user {getattr(user, 'id', 'unknown')}: {e}")
                    continue
            
            # Calculate average attendance percentage
            avg_attendance = sum(attendance_percentages) / len(attendance_percentages) if attendance_percentages else 0
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'results': summary_data,
                    'start_date': parsed_start.strftime('%Y-%m-%d'),
                    'end_date': parsed_end.strftime('%Y-%m-%d')
                })
            
            context = {
                'reports': summary_data,
                'total_present': total_present,
                'total_absent': total_absent,
                'total_late': total_late,
                'total_leave': total_leave,
                'total_hours': total_hours,
                'avg_attendance': round(avg_attendance, 1),
                'start_date': parsed_start.strftime('%Y-%m-%d'),
                'end_date': parsed_end.strftime('%Y-%m-%d'),
                'teachers': User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
            }
            
            return render(request, 'attendance/reports_results.html', context)
            
        except Exception as e:
            error_msg = f'Error generating attendance summary: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=500)
            else:
                messages.error(request, error_msg)
                return render(request, 'attendance/reports.html')
            

@method_decorator(headmaster_required, name='dispatch')
class ExportAttendancePDFView(LoginRequiredMixin, View):
    """Export attendance summary as PDF"""
    
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return HttpResponse('Invalid date format. Use YYYY-MM-DD.', status=400)
        
        # Validate date range
        if start_date > end_date:
            return HttpResponse('Start date cannot be after end date.', status=400)
        
        try:
            # Get summary data
            summary = get_attendance_summary(start_date, end_date)
            
            # Convert queryset to list of dicts for template
            summary_data = []
            total_present = 0
            total_absent = 0
            total_late = 0
            total_leave = 0
            
            for user in summary:
                try:
                    present_days = getattr(user, 'present_days', 0)
                    absent_days = getattr(user, 'absent_days', 0)
                    late_days = getattr(user, 'late_days', 0)
                    leave_days = getattr(user, 'leave_days', 0)
                    
                    # Add to totals
                    total_present += present_days
                    total_absent += absent_days
                    total_late += late_days
                    total_leave += leave_days
                    
                    summary_data.append({
                        'user_id': getattr(user, 'id', 0),
                        'user_name': f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
                        'department': getattr(user, 'department', ''),
                        'total_work_days': getattr(user, 'total_work_days', 0),
                        'present_days': present_days,
                        'absent_days': absent_days,
                        'late_days': late_days,
                        'leave_days': leave_days,
                        'half_days': getattr(user, 'half_days', 0),
                        'work_hours': float(getattr(user, 'work_hours', 0) or 0),
                        'attendance_percentage': round(float(getattr(user, 'attendance_percentage', 0) or 0), 2),
                    })
                except Exception as e:
                    print(f"Error processing user for PDF: {e}")
                    continue
            
            # Generate current timestamp for the report
            report_generated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Render HTML for PDF
            html_string = render_to_string('attendance/pdf_template.html', {
                'reports': summary_data,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'report_generated': report_generated,
                'total_teachers': len(summary_data),
                'total_present': total_present,
                'total_absent': total_absent,
                'total_late': total_late,
                'total_leave': total_leave,
            })
            
            # Generate PDF using WeasyPrint
            pdf_file = weasyprint.HTML(string=html_string).write_pdf()
            
            # Create response with PDF
            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f'attendance_report_{start_date.strftime("%Y%m%d")}_to_{end_date.strftime("%Y%m%d")}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error generating PDF: {str(e)}', status=500)
        
        
# ---- Dashboard/Analytics Views ----
@method_decorator(headmaster_required, name='dispatch')
class AttendanceDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view with attendance analytics"""
    template_name = 'attendance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current month data
        today = datetime.now().date()
        first_day_of_month = today.replace(day=1)
        
        # Basic statistics
        total_teachers = User.objects.filter(user_type='teacher').count()
        total_records_this_month = Attendance.objects.filter(
            date__gte=first_day_of_month,
            date__lte=today
        ).count()
        
        # Recent attendance records
        recent_attendance = Attendance.objects.select_related('teacher').order_by('-date', '-created_at')[:10]
        
        context.update({
            'total_teachers': total_teachers,
            'total_records_this_month': total_records_this_month,
            'recent_attendance': recent_attendance,
            'current_month': today.strftime('%B %Y'),
        })
        
        return context


# ---- Bulk Operations Views ----
@method_decorator(headmaster_required, name='dispatch')
class BulkAttendanceCreateView(LoginRequiredMixin, TemplateView):
    """View for creating attendance records for multiple teachers at once"""
    template_name = 'attendance/bulk_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(user_type='teacher').order_by('first_name', 'last_name')
        context['today'] = datetime.now().date().strftime('%Y-%m-%d')
        
        from .models import ATTENDANCE_STATUSES
        context['status_choices'] = ATTENDANCE_STATUSES.choices
        
        return context
    
    def post(self, request):
        """Handle bulk attendance creation"""
        try:
            date_str = request.POST.get('date')
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            created_count = 0
            errors = []
            
            for teacher in User.objects.filter(user_type='teacher'):
                status = request.POST.get(f'status_{teacher.id}')
                check_in = request.POST.get(f'check_in_{teacher.id}')
                check_out = request.POST.get(f'check_out_{teacher.id}')
                remarks = request.POST.get(f'remarks_{teacher.id}', '')
                
                if status:  # Only create if status is selected
                    try:
                        # Check if record already exists
                        existing = Attendance.objects.filter(
                            teacher=teacher,
                            date=attendance_date
                        ).exists()
                        
                        if not existing:
                            # Calculate week number
                            week_num = attendance_date.isocalendar()[1]
                            
                            Attendance.objects.create(
                                teacher=teacher,
                                date=attendance_date,
                                week_num=week_num,
                                status=status,
                                check_in_time=check_in if check_in else None,
                                check_out_time=check_out if check_out else None,
                                remarks=remarks
                            )
                            created_count += 1
                        else:
                            errors.append(f"Record for {teacher.get_full_name()} already exists")
                            
                    except Exception as e:
                        errors.append(f"Error creating record for {teacher.get_full_name()}: {str(e)}")
            
            if created_count > 0:
                messages.success(request, f'Successfully created {created_count} attendance records.')
            
            if errors:
                for error in errors:
                    messages.warning(request, error)
            
            return render(request, self.template_name, self.get_context_data())
            
        except Exception as e:
            messages.error(request, f'Error processing bulk attendance: {str(e)}')
            return render(request, self.template_name, self.get_context_data())