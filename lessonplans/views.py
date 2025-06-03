
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Q, Count
from .models import LessonPlan, LessonPlanCheck
from .forms import LessonPlanForm, LessonPlanSearchForm, LessonPlanStep1Form, LessonPlanStep2Form, LessonPlanStep3Form, LessonPlanCheckForm
from formtools.wizard.views import SessionWizardView
from xhtml2pdf import pisa
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce


class LessonPlanListView(LoginRequiredMixin, ListView):
    model = LessonPlan
    template_name = 'lessons/lesson_list.html'
    context_object_name = 'lessons'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.user_type == 'headmaster':
            queryset = LessonPlan.objects.all() # Headmasters see all plans
        else:
            queryset = LessonPlan.objects.filter(created_by=self.request.user) # Teachers see only their own
        form = LessonPlanSearchForm(self.request.GET)
        
        if form.is_valid():
            search = form.cleaned_data.get('search')
            subject = form.cleaned_data.get('subject')
            grade_level = form.cleaned_data.get('grade_level')
            
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(subject__icontains=search) |
                    Q(key_words__icontains=search)
                )
            
            if subject:
                queryset = queryset.filter(subject__icontains=subject)
            
            if grade_level:
                queryset = queryset.filter(grade_level__icontains=grade_level)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = LessonPlanSearchForm(self.request.GET)
        return context

class LessonPlanDetailView(LoginRequiredMixin, DetailView):
    model = LessonPlan
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        if self.request.user.user_type == 'headmaster':
            return LessonPlan.objects.all()  # Headmasters can view any lesson plan
        else:
            return LessonPlan.objects.filter(created_by=self.request.user) # Teachers can only view their own
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If the user is a headmaster, find their specific review for this lesson plan
        if self.request.user.user_type == 'headmaster':
            context['user_review'] = LessonPlanCheck.objects.filter(
                lesson_plan=self.object, # self.object is the LessonPlan instance being viewed
                checked_by=self.request.user
            ).first()
        return context
    

@method_decorator(login_required, name='dispatch')
class LessonPlanWizard(SessionWizardView):
    template_name = 'lessons/lesson_plan_wizard.html'
    form_list = [LessonPlanStep1Form, LessonPlanStep2Form, LessonPlanStep3Form]
    
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['title'] = "Create Lesson Plan"
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Lesson plan created successfully!')
        return super().form_valid(form)
    
    def done(self, form_list, **kwargs):
        instance = LessonPlan()
        instance.created_by = self.request.user
        for form in form_list:
            for field, value in form.cleaned_data.items():
                setattr(instance, field, value)
        instance.save()
        return HttpResponseRedirect(reverse_lazy('lessonplans:lesson_detail', kwargs={'pk': instance.pk}))

class LessonPlanCreateView(LoginRequiredMixin, CreateView):
    model = LessonPlan
    form_class = LessonPlanForm
    template_name = 'lessons/lesson_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Lesson plan created successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class LessonPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = LessonPlan
    form_class = LessonPlanForm
    template_name = 'lessons/lesson_form.html'

    def get_queryset(self):
        return LessonPlan.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Lesson plan updated successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class LessonPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = LessonPlan
    template_name = 'lessons/lesson_confirm_delete.html'
    success_url = reverse_lazy('lesson_list')

    def get_queryset(self):
        return LessonPlan.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Lesson plan deleted successfully!')
        return super().delete(request, *args, **kwargs)


def export_lessonplan_pdf(request, pk):
    lesson = get_object_or_404(LessonPlan, pk=pk, created_by=request.user)
    template = get_template('lessons/lessonplan_pdf.html')
    html = template.render({'lesson': lesson})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lessonplan_{lesson.pk}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def check_lesson_plan(request, pk):
    lesson_plan = get_object_or_404(LessonPlan, pk=pk)
    check_instance = LessonPlanCheck.objects.filter(
        lesson_plan=lesson_plan,
        checked_by=request.user
    ).first()

    if request.method == 'POST':
        form = LessonPlanCheckForm(request.POST, instance=check_instance)
        if form.is_valid():
            check = form.save(commit=False)
            check.lesson_plan = lesson_plan
            check.checked_by = request.user
            check.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('lessonplans:lesson_detail', pk=pk)
    else:
        form = LessonPlanCheckForm(instance=check_instance)

    return render(request, 'lessons/check_form.html', {
        'lesson_plan': lesson_plan,
        'form': form
    })

@login_required
def export_all_lessonplans_status_pdf(request):
    if request.user.user_type != 'headmaster':
        # Optionally, return a 403 Forbidden or redirect to a 'permission denied' page
        messages.error(request, "You do not have permission to access this report.")
        return redirect('lessonplans:lesson_list') # Or any other appropriate URL

    # Subquery to get the status of the latest check for each lesson plan
    latest_check_status = LessonPlanCheck.objects.filter(
        lesson_plan=OuterRef('pk')
    ).order_by('-date_checked').values('status')[:1]

    lesson_plans = LessonPlan.objects.annotate(
        latest_status=Coalesce(Subquery(latest_check_status), Value('Not Reviewed'))
    ).order_by('date_created')

    # Prepare context for the template
    context = {
        'lesson_plans': [],
        'report_date': timezone.now()
    }

    for plan in lesson_plans:
        status_display = plan.latest_status
        if plan.latest_status != 'Not Reviewed':
            # Get the display value for the status if it's a choice field
            # Assuming LessonPlanCheck.STATUS_CHOICES is defined in your model
            status_dict = dict(LessonPlanCheck.STATUS_CHOICES)
            status_display = status_dict.get(plan.latest_status, plan.latest_status)
        
        context['lesson_plans'].append({
            'title': plan.title,
            'created_by': plan.created_by.get_full_name() or plan.created_by.username,
            'date_created': plan.date_created,
            'status': status_display,
            'subject': plan.subject,
            'grade_level': plan.grade_level,
        })

    template_path = 'lessons/lessonplan_status_report_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lessonplan_status_report_{timezone.now().strftime("%Y-%m-%d")}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors &lt;pre&gt;' + html + '&lt;/pre&gt;')
    return response