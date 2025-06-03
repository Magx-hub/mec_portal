from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
import secrets
import string
from .models import User
from .forms import UserForm
from lessonplans.models import LessonPlan
from attendance.models import Attendance
from .decorators import headmaster_required

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect to dashboard after successful login
        return reverse_lazy('users:dashboard')

class UserLogoutView(LogoutView):
    """
    User logout view with custom messaging.
    The next_page is set in settings.py with LOGOUT_REDIRECT_URL.
    """
    template_name = 'users/logout.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - show logout confirmation page"""
        return self.render_to_response({})
    
    def post(self, request, *args, **kwargs):
        """Handle POST request - perform logout"""
        if request.user.is_authenticated:
            messages.info(request, 'You have been successfully logged out.')
        return super().post(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'teacher':
            context['lesson_plans'] = LessonPlan.objects.filter(created_by=user)[:5]  # Recent 5
            context['attendance'] = Attendance.objects.filter(teacher=user)[:5]  # Recent 5
            context['lesson_count'] = LessonPlan.objects.filter(created_by=user).count()
            context['attendance_count'] = Attendance.objects.filter(teacher=user).count()
        elif user.user_type == 'headmaster':
            context['lesson_plans'] = LessonPlan.objects.all()[:5]  # Recent 5
            context['attendance'] = Attendance.objects.all()[:5]  # Recent 5
            context['teachers'] = User.objects.filter(user_type='teacher')
            context['lesson_count'] = LessonPlan.objects.count()
            context['attendance_count'] = Attendance.objects.count()
            context['total_teachers'] = User.objects.filter(user_type='teacher').count()
            
        return context

# User Management Views - Headmaster Only

@method_decorator(headmaster_required, name='dispatch')
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['first_name', 'last_name']
    paginate_by = 20  # Add pagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = self.get_queryset().count()
        context['total_teachers'] = self.get_queryset().filter(user_type='teacher').count()
        context['total_headmasters'] = self.get_queryset().filter(user_type='headmaster').count()
        context['search_query'] = self.request.GET.get('search', '')
        return context

@method_decorator(headmaster_required, name='dispatch')
class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_update'] = False
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New User'
        context['form_submit_text'] = 'Create User'
        context['is_update'] = False
        return context
    
    def form_valid(self, form):
        user = form.save(commit=False)
        # Generate secure random password
        default_password = generate_secure_password()
        user.set_password(default_password)
        user.save()
        
        # Store password in session for secure display (don't log it)
        self.request.session['temp_password'] = default_password
        self.request.session['temp_username'] = user.username
        
        messages.success(
            self.request, 
            f'User {user.username} has been created successfully. '
            'Please check the password information below and share it securely with the user.'
        )
        return redirect('users:user-password-display')



@method_decorator(headmaster_required, name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_update'] = True
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Update User: {self.object.username}'
        context['form_submit_text'] = 'Update User'
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'User {user.username} has been updated successfully.')
        return super().form_valid(form)

@method_decorator(headmaster_required, name='dispatch')
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user-list')
    context_object_name = 'user'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Prevent self-deletion
        if obj == self.request.user:
            raise PermissionDenied("You cannot delete your own account.")
        return obj
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'User {username} has been deleted successfully.')
        return response


@method_decorator(headmaster_required, name='dispatch')
class UserResetPasswordView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/user_reset_password.html'
    fields = []  # No fields needed as we're just resetting the password
    success_url = reverse_lazy('users:user-list')
    
    def form_valid(self, form):
        user = self.get_object()
        # Generate secure random password
        new_password = generate_secure_password()
        user.set_password(new_password)
        user.save()
        
        # Store password in session for secure display
        self.request.session['temp_password'] = new_password
        self.request.session['temp_username'] = user.username
        
        messages.success(
            self.request, 
            f'Password for {user.username} has been reset successfully. '
            'Please check the password information below.'
        )
        return redirect('users:user-password-display')


@method_decorator(headmaster_required, name='dispatch')
class UserPasswordDisplayView(LoginRequiredMixin, TemplateView):
    """Secure display of newly created user password"""
    template_name = 'users/user_password_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temp_password = self.request.session.get('temp_password')
        temp_username = self.request.session.get('temp_username')

        if not temp_password or not temp_username:
            messages.error(self.request, 'Password information has expired or is unavailable.')
            context['temp_password'] = None
            context['temp_username'] = None
        else:
            context['temp_password'] = temp_password
            context['temp_username'] = temp_username
            # Remove from session after displaying once
            self.request.session.pop('temp_password', None)
            self.request.session.pop('temp_username', None)

        return context
    

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password-change-done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Change Your Password'
        context['form_submit_text'] = 'Change Password'
        return context

class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'users/password_change_done.html'

# Utility Views
class ComingSoonView(TemplateView):
    template_name = 'future/coming_soon.html'

class WeeklyPerformanceMonitor(TemplateView):
    template_name = 'future/coming_soon.html'