# content/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django import forms

from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings

from .models import (
    Post, Project, ProjectDocument, Category, Tag, Volunteer,
    MembershipPayment, MemberProfile, CustomUser, Suggestion
)
from .forms import (
    CustomSignupForm, CustomLoginForm, EmailChangeForm,
    PaymentForm, SuggestionForm, ProjectForm
)
from .utils import role_required, RoleRequiredMixin

User = get_user_model()

# ------------------------
# ProjectDocument inline formset
# ------------------------
ProjectDocumentFormSet = inlineformset_factory(
    Project,
    ProjectDocument,
    fields=('title', 'file'),
    extra=1,
    can_delete=True
)

# ========================
# Account / Profile Views
# ========================
class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "content/delete_account.html"
    success_url = reverse_lazy("home")

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Your account has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = "content/profile.html"


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_image']


@method_decorator(login_required, name='dispatch')
class SettingsView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "content/settings.html"
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


# ========================
# Auth / Signup / Login
# ========================
class SignupView(View):
    form_class = CustomSignupForm
    template_name = 'content/signup.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(request)
            return complete_signup(
                request,
                user,
                allauth_settings.EMAIL_VERIFICATION,
                redirect_url='/'
            )
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})


class LoginView(AllauthLoginView):
    template_name = 'account/login.html'


# ========================
# Search & Filter Mixin
# ========================
class SearchAndFilterMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        tag = self.request.GET.get('tag')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(summary__icontains=q) |
                Q(body__icontains=q)
            )
        if cat:
            qs = qs.filter(category__slug=cat)
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['tags'] = Tag.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['current_category'] = self.request.GET.get('category', '')
        ctx['current_tag'] = self.request.GET.get('tag', '')
        return ctx


# ========================
# Blog / News / Volunteer Views
# ========================
class BlogListView(SearchAndFilterMixin, ListView):
    queryset = Post.objects.filter(type=Post.BLOG, is_published=True)
    template_name = 'content/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6


class BlogDetailView(DetailView):
    model = Post
    template_name = 'content/blog_detail.html'
    context_object_name = 'post'


class NewsListView(SearchAndFilterMixin, ListView):
    queryset = Post.objects.filter(type=Post.NEWS, is_published=True)
    template_name = 'content/news_list.html'
    context_object_name = 'posts'
    paginate_by = 6


class NewsDetailView(DetailView):
    model = Post
    template_name = 'content/news_detail.html'
    context_object_name = 'post'


class ProjectListView(ListView):
    model = Project
    template_name = 'content/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'content/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'       # The field in your model
    slug_url_kwarg = 'slug'   # The URL parameter


class VolunteerListView(ListView):
    model = Volunteer
    template_name = 'content/volunteer_list.html'
    context_object_name = 'volunteers'


# ========================
# Post CRUD (role protected)
# ========================
class PostCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Post
    fields = ['title', 'type', 'summary', 'body', 'category', 'tags', 'cover_image', 'is_published', 'published_at']
    template_name = 'content/post_form.html'
    success_url = reverse_lazy('blog_list')


class PostUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Post
    fields = ['title', 'type', 'summary', 'body', 'category', 'tags', 'cover_image', 'is_published', 'published_at']
    template_name = 'content/post_form.html'
    success_url = reverse_lazy('blog_list')


class PostDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Post
    template_name = 'content/post_confirm_delete.html'
    success_url = reverse_lazy('blog_list')


# ========================
# Project CRUD (class-based)
# ========================
class ProjectCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Project
    form_class = ProjectForm
    template_name = "content/project_form.html"
    success_url = reverse_lazy('project_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProjectDocumentFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ProjectDocumentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        messages.success(self.request, "Project created successfully!")
        return super().form_valid(form)


class ProjectUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Project
    form_class = ProjectForm
    template_name = "content/project_form.html"
    success_url = reverse_lazy('project_list')
    slug_field = 'slug'       # The field in your model
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProjectDocumentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = ProjectDocumentFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.save()
        messages.success(self.request, "Project updated successfully!")
        return super().form_valid(form)


class ProjectDeleteView(RoleRequiredMixin, LoginRequiredMixin, DeleteView):
    allowed_roles = ('admin', 'manager', 'staff')
    model = Project
    template_name = "content/project_confirm_delete.html"
    success_url = reverse_lazy('project_list')
    slug_field = 'slug'       # The field in your model
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Project deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ========================
# Email Change View
# ========================
class EmailChangeView(LoginRequiredMixin, UpdateView):
    form_class = EmailChangeForm
    template_name = "content/email_change.html"
    success_url = reverse_lazy("settings")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your email has been updated successfully.")
        return super().form_valid(form)


# ========================
# Dashboard View
# ========================
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = "content/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Statistics
        context['projects_count'] = Project.objects.count()
        context['news_count'] = Post.objects.filter(type=Post.NEWS, is_published=True).count()
        context['blogs_count'] = Post.objects.filter(type=Post.BLOG, is_published=True).count()
        context['volunteers_count'] = Volunteer.objects.count()

        # User profile
        profile, _ = MemberProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        context['user'] = user

        current_year = timezone.now().year
        verified_total = MembershipPayment.objects.filter(
            user=user, status='verified', year=current_year
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        context['verified_total_this_year'] = verified_total
        context['annual_fee'] = getattr(MembershipPayment, 'ANNUAL_FEE', None) or 50000
        context['user_balance'] = max(context['annual_fee'] - verified_total, 0)

        # Suggestions
        context['suggestions'] = Suggestion.objects.select_related('user').order_by('-created_at')[:50]
        context['suggestion_form'] = SuggestionForm()

        # Leader-only data
        leaders = ('admin', 'manager', 'staff')
        if getattr(user, 'ngo_role', None) in leaders or user.is_superuser:
            context['members_summary'] = CustomUser.objects.all().order_by('username')
            context['members_total'] = CustomUser.objects.count()
            context['active_members_count'] = MemberProfile.objects.filter(is_active_member=True).count()
            context['inactive_members_count'] = MemberProfile.objects.filter(is_active_member=False).count()
            context['pending_payments'] = MembershipPayment.objects.filter(status='pending').order_by('-date_submitted')[:100]
        else:
            context['members_summary'] = None
            context['pending_payments'] = None

        return context

    def post(self, request, *args, **kwargs):
        form = SuggestionForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.user = request.user
            s.save()
            messages.success(request, "Asante — suggestion yako imepokelewa.")
            return redirect(request.path)
        context = self.get_context_data(**kwargs)
        context['suggestion_form'] = form
        return render(request, self.template_name, context)


# ========================
# Members list
# ========================
@role_required('admin', 'manager', 'staff')
def members_list(request):
    members = CustomUser.objects.all().order_by('username')
    profiles = MemberProfile.objects.select_related('user').all()
    return render(request, 'content/members_list.html', {'members': members, 'profiles': profiles})


# ========================
# Payment Views
# ========================
@login_required
def make_payment(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    if not profile.control_number:
        profile.generate_control_number()

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.status = 'pending'
            payment.amount_paid = getattr(MembershipPayment, 'ANNUAL_FEE', None) or 50000
            payment.year = timezone.now().year
            payment.save()
            messages.success(request, "Payment submitted. Awaiting bank verification.")
            return redirect('dashboard')
    else:
        form = PaymentForm(initial={'payment_method': 'bank_transfer'})

    bank_info = {
        'bank_name': 'CRDB Bank PLC',
        'account_name': 'OnePlus Resilience Organization',
        'account_number': '01J100xxxxxxx',
        'amount': getattr(MembershipPayment, 'ANNUAL_FEE', None) or 50000,
        'reference_hint': profile.control_number,
        'instructions': "Please use your unique control number as payment reference."
    }

    return render(request, 'membership/payment_form.html', {'form': form, 'bank_info': bank_info, 'profile': profile})


@role_required('admin', 'staff')
def verify_payment(request, pk):
    payment = get_object_or_404(MembershipPayment, pk=pk)
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            payment.status = 'verified'
            payment.verified_by = user
            payment.verified_at = timezone.now()
            if not payment.date_paid:
                payment.date_paid = timezone.now().date()
            payment.save()
            profile, _ = MemberProfile.objects.get_or_create(user=payment.user)
            profile.last_payment_date = payment.date_paid
            profile.update_membership_status()
            messages.success(request, "Payment verified successfully.")
            return redirect('dashboard')
        elif action == 'reject':
            payment.status = 'failed'
            payment.verified_by = user
            payment.verified_at = timezone.now()
            payment.save()
            messages.info(request, "Payment rejected / marked as failed.")
            return redirect('dashboard')

    return render(request, 'membership/verify_payment.html', {'payment': payment})


@role_required('admin', 'manager', 'staff')
def payments_list(request):
    payments = MembershipPayment.objects.all().order_by('-date_submitted')
    return render(request, 'membership/payments_list.html', {'payments': payments})


# ========================
# Suggestion Views
# ========================
@login_required
def suggestion_list(request):
    suggestions = Suggestion.objects.select_related('user').order_by('-created_at')
    return render(request, 'content/suggestions_list.html', {'suggestions': suggestions})
 