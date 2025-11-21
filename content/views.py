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
from datetime import timedelta
from datetime import datetime
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from decimal import Decimal
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin


# === HAKIKISHA HIZI IMPORTS ZINAKUWA SAHIHI KUTOKA KWENYE MODULE MOJA (content) ===
from .models import (
    Post, Project, ProjectDocument, Category, Tag, Volunteer,Meeting,
    MembershipPayment, MemberProfile, CustomUser, Suggestion, ANNUAL_FEE
)
from .forms import (
    CustomSignupForm, CustomLoginForm, EmailChangeForm,
    PaymentForm, SuggestionForm, ProjectForm
)
# Hizi zimetajwa kuwa ziko hapa au unazi-import kutoka sehemu nyingine
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
# Dashboard View (REVISED)
# ========================
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = "content/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        upcoming_meetings = Meeting.objects.filter(
        Q(organizer=user) | Q(attendees=user),
        end_time__gt=datetime.now() # Mikutano ambayo bado haijaisha
         ).distinct().order_by('start_time')[:3] # Chukua 3 za kwanza tu

        context['upcoming_meetings'] = upcoming_meetings

        # User profile and financial status
        profile, _ = MemberProfile.objects.get_or_create(user=user)
        # 1. Update membership status on every dashboard load to ensure accuracy
        profile.update_membership_status() 
        context['profile'] = profile
        context['user'] = user

        # Malipo na Ada
        context['annual_fee'] = ANNUAL_FEE # Decimal value
        
        # 2. KUONYESHA ONYO KWA MALIPO YA AWAMU YALIYOISHA MUDA WAKE
        # *Hii inatumia property ya is_active_member na total_verified_paid_this_year kutoka models.py*
        if not profile.is_active_member and profile.total_verified_paid_this_year > Decimal('0.00'):
            messages.warning(
                self.request,
                "⚠️ **Tahadhari:** Uanachama wako umefikia kikomo (Expired) licha ya kufanya malipo ya awamu. "
                "Ili kuamilisha tena uanachama wako au kulipa salio, **tafadhali wasiliana na Admin/Muhasibu** mara moja."
            )
        
        # 3. Hundi ya malipo yanayosubiri uhakiki
        current_year = timezone.now().year
        context['has_pending_payment'] = MembershipPayment.objects.filter(
            user=user, 
            status='pending',
            year=current_year 
        ).exists()
        
        # Statistics
        context['projects_count'] = Project.objects.count()
        context['news_count'] = Post.objects.filter(type=Post.NEWS, is_published=True).count()
        context['blogs_count'] = Post.objects.filter(type=Post.BLOG, is_published=True).count()
        context['volunteers_count'] = Volunteer.objects.count()

        # Suggestions
        context['suggestions'] = Suggestion.objects.select_related('user').order_by('-created_at')[:50]
        context['suggestion_form'] = SuggestionForm()

        # Leader-only data
        leaders = ('admin', 'manager', 'staff')
        if getattr(user, 'ngo_role', None) in leaders or user.is_superuser:
            context['members_summary'] = CustomUser.objects.all().order_by('username')
            context['members_total'] = CustomUser.objects.count()
            
            # 4. HESABU SAHIHI ZA ACTIVE/INACTIVE MEMBERS (Kutumia expiry_date)
            today = timezone.now().date()
            active_members = MemberProfile.objects.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today
            )
            context['active_members_count'] = active_members.count()
            
            # Inactive = Hakuna expiry_date AU expiry_date imepita
            inactive_members = MemberProfile.objects.filter(
                Q(expiry_date__isnull=True) | Q(expiry_date__lt=today)
            )
            context['inactive_members_count'] = inactive_members.count()
            
            context['pending_payments'] = MembershipPayment.objects.filter(status='pending').order_by('-date_submitted')[:100]
        else:
            context['members_summary'] = None
            context['pending_payments'] = None

        return context

    def post(self, request, *args, **kwargs):
        """Handles suggestion form submission."""
        form = SuggestionForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.user = request.user
            s.save()
            messages.success(request, "Asante — suggestion yako imepokelewa.")
            return redirect(request.path)
            
        # Re-render the dashboard with form errors if invalid
        context = self.get_context_data(**kwargs)
        context['suggestion_form'] = form
        return render(request, self.template_name, context)
# ========================
# Payment Views (REVISED WITH PERMISSION CHECKS)
# ========================
@login_required
def make_payment(request):
    """View to handle submitting new payment proof."""
    profile, created = MemberProfile.objects.get_or_create(user=request.user)
    
    # Ensure control number exists
    if created or not profile.control_number:
        # Tuseme hii method ipo kwenye MemberProfile model
        profile.generate_control_number() 

    if request.method == 'POST':
        # Kumbuka: PaymentForm inatakiwa kuwa na fields za amount, reference, date_paid, na proof_image
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Data za ziada kutoka kwenye form fields za ziada
            # NB: Hizi zinatakiwa kuwepo kwenye PaymentForm
            payment.amount_paid = form.cleaned_data.get('amount')
            payment.reference = form.cleaned_data.get('reference')
            payment.date_paid = form.cleaned_data.get('date_paid')
            
            # Data zinazohitajika za model
            payment.user = request.user
            payment.status = 'pending' # Uhakiki wa mikono (Manual Verification)
            payment.year = timezone.now().year
            
            payment.save()
            messages.success(request, f"Malipo ya awamu ya TZS {payment.amount_paid:,.2f} yamewasilishwa. Inasubiri uhakiki wa admin.")
            return redirect('make_payment') 
            
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if form.fields[field].label else field.replace('_', ' ').title()
                    messages.error(request, f"Kuna kosa katika {field_label}: {error}")
            
    else:
        initial_data = {
            'date_paid': timezone.now().date(),
        }
        form = PaymentForm(initial=initial_data)

    bank_info = {
        'bank_name': 'CRDB Bank PLC',
        'account_name': 'OnePlus Resilience Organization',
        'account_number': '01J100xxxxxxx',
        'annual_fee': ANNUAL_FEE,
        'reference_hint': profile.control_number if profile.control_number else 'Generate control number first',
        'instructions': "Tafadhali tumia Control Number yako kama kumbukumbu ya malipo."
    }
    
    # Tunapata malipo yote kwa ajili ya orodha ya muhtasari
    all_payments = MembershipPayment.objects.filter(user=request.user).order_by('-date_submitted')

    return render(request, 'membership/payment_form.html', {
        'form': form, 
        'bank_info': bank_info, 
        'profile': profile,
        'all_payments': all_payments, 
        'ANNUAL_FEE': ANNUAL_FEE,
    })


@login_required 
def verify_payment(request, payment_pk):
    """
    Admin/Staff view to verify or reject a payment.
    Inaongeza siku 90 kwa kila malipo ya awamu yanayozidi MINIMUM_INSTALLMENT_FEE 
    hadi malipo kamili yafikiwe.
    """
    leaders = ('admin', 'accountant')
    if not (getattr(request.user, 'ngo_role', None) in leaders or request.user.is_superuser):
         messages.error(request, "Huna ruhusa ya kuona ukurasa huu.")
         return redirect('dashboard') 

    payment = get_object_or_404(MembershipPayment, pk=payment_pk)

    if payment.status != 'pending':
         messages.warning(request, f"Malipo ID {payment_pk} tayari yamekuwa {payment.get_status_display()}.")
         return redirect('payment_list') 
         
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Import constants (lazima uwe umeziweka kwenye models.py kama tulivyokubaliana)
        from .models import MINIMUM_INSTALLMENT_FEE, DAYS_PER_INSTALLMENT, ANNUAL_FEE
        
        try:
            profile, _ = MemberProfile.objects.get_or_create(user=payment.user)
            
            if action == 'verify':
                # 1. Update Payment Record
                payment.status = 'verified'
                payment.verified_by = user
                payment.verified_at = timezone.now()
                if not payment.date_paid:
                     payment.date_paid = timezone.now().date()
                payment.save()
                
                amount_paid_decimal = payment.amount_paid
                
                # 2. Update Member Status: Kuongeza Muda wa Uanachama (Expiry Date)
                
                # Sasa tunatumia method ya profile.update_membership_status() 
                # ili kuangalia malipo yote kwa mwaka.
                
                # MANTIKI YA AWAMU:
                # Ikiwa kiasi kilicholipwa sasa kinakidhi kiwango cha awamu (TZS 12,500)
                # na jumla ya malipo HAJAFIKISHA ada kamili:
                if amount_paid_decimal >= MINIMUM_INSTALLMENT_FEE and profile.total_verified_paid_this_year < ANNUAL_FEE:
                    
                    current_expiry = profile.expiry_date
                    today = timezone.now().date()
                    
                    # Anza kuongeza kutoka sasa au tarehe ya mwisho ya uanachama (ikiwa bado haijapita)
                    if current_expiry is None or current_expiry < today:
                        start_date = today
                    else:
                        start_date = current_expiry
                        
                    # Ongeza siku 90 kwa kila awamu (12,500 TZS) aliyolipia kwa malipo haya.
                    # Hata hivyo, kwa kuwa ameweka malipo yote kama awamu (partial), 
                    # tunaongeza siku 90 kwa malipo ya kwanza tu, na mengine yanabaki kama partial payment.
                    # Ni salama zaidi kuongeza siku 90 tu kwa malipo ya kwanza ya awamu.
                    
                    # Njia rahisi: Ongeza siku 90 kila Admin anapothibitisha Awamu ya kutosha.
                    
                    # A) Kama total_verified_paid_this_year ni sawa au inazidi awamu kamili
                    installments_paid = int(profile.total_verified_paid_this_year / MINIMUM_INSTALLMENT_FEE)
                    
                    # B) Piga hesabu ya uanachama kwa siku (Miezi 3 x idadi ya Awamu)
                    # Hii inahitaji `MemberProfile` kuhifadhi ni kiasi gani cha malipo kimetumika.
                    
                    # TUTARUDI KWENYE LOGIC SAFI:
                    
                    # 1. Piga hesabu ya siku za uanachama kwa malipo YOTE yaliyothibitishwa (Awamu NNE tu)
                    
                    total_installments = int(profile.total_verified_paid_this_year / MINIMUM_INSTALLMENT_FEE)
                    
                    # Muda wa Uanachama unaostahili (kwa siku)
                    deserved_days = total_installments * DAYS_PER_INSTALLMENT
                    
                    # Muda wa Uanachama Kamili (kwa siku)
                    full_membership_days = 4 * DAYS_PER_INSTALLMENT # 360 days
                    
                    # Muda wa juu (maximum) kwa malipo ya awamu ni siku 360
                    if deserved_days > full_membership_days:
                        deserved_days = full_membership_days
                        
                    # 2. Kuweka expiry date: Anza kuhesabu kutoka tarehe ya malipo ya kwanza ya mwaka
                    first_payment_of_year = MembershipPayment.objects.filter(
                        user=payment.user,
                        status='verified',
                        year=payment.year 
                    ).order_by('date_paid').first()
                    
                    if first_payment_of_year and first_payment_of_year.date_paid:
                        start_date_for_renewal = first_payment_of_year.date_paid
                        profile.expiry_date = start_date_for_renewal + timedelta(days=deserved_days)
                        profile.last_payment_date = payment.date_paid
                        profile.save(update_fields=['expiry_date', 'last_payment_date'])
                        
                    # Ikiwa amemaliza ada kamili (TZS 50,000), `update_membership_status` itaiweka kuwa 365 days.
                
                # 3. Ikiisha (Malipo kamili yametimizwa au hayajatimizwa), sasisha hadhi kwa ujumla
                profile.update_membership_status() 
                
                messages.success(request, f"Malipo {payment.id} yamethibitishwa kwa mafanikio. Hadhi ya Mwanachama imesasishwa.")
            
            elif action == 'reject':
                # ... (reject logic inabaki jinsi ilivyo) ...
                payment.status = 'failed'
                payment.verified_by = user
                payment.verified_at = timezone.now()
                payment.save()
                
                profile.update_membership_status() 
                
                messages.info(request, f"Malipo {payment.id} yamekataliwa.")
            
            return redirect('payment_list') 

        except Exception as e:
            messages.error(request, f"Kosa limetokea wakati wa uhakiki: {e}")
            # Hakikisha una URL ya 'payments_list' au 'payment_list'
            return redirect('payment_list')
    
    return render(request, 'membership/verify_payment.html', {'payment': payment})

@login_required
def payments_list(request):
    """Admin/Staff view for listing all payments."""
    leaders = ('admin', 'accountant')
    if not (getattr(request.user, 'ngo_role', None) in leaders or request.user.is_superuser):
          messages.error(request, "Huna ruhusa ya kuona ukurasa huu.")
          return redirect('dashboard') 
          
    payments = MembershipPayment.objects.all().order_by('-date_submitted')
    pending_payments = payments.filter(status='pending') # Ongeza hii
    
    pending_count = pending_payments.count()
    
    return render(request, 'membership/payments_list.html', {
        'payments': payments, # Orodha yote
        'pending_payments': pending_payments, # Orodha ya kusubiri pekee (Kwa ajili ya Tab 1)
        'pending_count': pending_count
    })


# ========================
# Suggestion Views
# ========================
@login_required
def suggestion_list(request):
    """Admin/Staff view for listing all suggestions."""
    leaders = ('admin', 'manager', 'staff')
    if not (getattr(request.user, 'ngo_role', None) in leaders or request.user.is_superuser):
         messages.error(request, "Huna ruhusa ya kuona ukurasa huu.")
         return redirect('dashboard') 
         
    suggestions = Suggestion.objects.select_related('user').order_by('-created_at')
    return render(request, 'content/suggestions_list.html', {'suggestions': suggestions})





# ... (Hakikisha User inapitisha CustomUser)
User = get_user_model() 

# Hiki ni kipande cha msimbo wako wa views.py
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'content/user_list.html' 
    context_object_name = 'users'
    ordering = ['username']
    paginate_by = 50

    def test_func(self):
        # Ruhusu tu watumiaji wenye majukumu haya kuona orodha
        leaders = ['admin', 'accountant', 'manager', 'staff', 'member'] # Nimeongeza 'member' ili kuwaona wote
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'ngo_role') and self.request.user.ngo_role in leaders
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Muda wa mwisho wa kuwa active (Sekunde 300 = Dakika 5)
        active_time_threshold = timezone.now() - timedelta(seconds=300) 
        context['active_time_threshold'] = active_time_threshold
        
        # Hii ni muhimu kwa ajili ya kutathmini status kwenye template
        
        return context



# content/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin # Hakikisha hii ipo
# ... (Hakikisha Meeting model imeingizwa: from .models import ..., Meeting)
from .forms import MeetingForm # Hakikisha MeetingForm imeingizwa

# -------------------- Utility Mixins kwa ajili ya Permissions --------------------
class LeaderRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Inahakikisha mtumiaji ni Admin, Accountant, Manager, au Staff."""
    def test_func(self):
        leaders = ['admin', 'accountant', 'manager', 'staff']
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'ngo_role') and self.request.user.ngo_role in leaders
        )
    
    def handle_no_permission(self):
        messages.warning(self.request, "Huna ruhusa ya kufanya operesheni hii.")
        return redirect(reverse_lazy('dashboard')) # Rudi Dashboard
        
# -------------------- Meeting Views (CRUD) --------------------
class MeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'content/meetings/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 15

class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    template_name = 'content/meetings/meeting_detail.html'
    context_object_name = 'meeting'
    
    def get_queryset(self):
        # Mtu yeyote aliyeingia anaweza kuona meeting, lakini ataziona tu zile ambazo
        # aidha yeye ni organizer au attendee.
        if self.request.user.is_superuser or self.request.user.ngo_role in ['admin', 'accountant', 'manager', 'staff']:
             return Meeting.objects.all() # Viongozi wanaona zote
        
        return Meeting.objects.filter(
            Q(organizer=self.request.user) | Q(attendees=self.request.user)
        ).distinct()

class MeetingCreateView(LeaderRequiredMixin, CreateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'content/meetings/meeting_form.html'
    success_url = reverse_lazy('meeting_list')
    
    def form_valid(self, form):
        # 1. Marekebisho ya Datetime: Fanya end_time iwe timezone-aware
        # Fanya hivi KABLA ya form.save() au super().form_valid(form)
        end_time = form.cleaned_data.get('end_time')
        
        if end_time and timezone.is_naive(end_time):
            # Badilisha end_time kuwa aware na iingize kwenye mfano (instance)
            form.instance.end_time = timezone.make_aware(end_time)

        # RUPIA KWA start_time (kama inahitajika/inaleta onyo)
        start_time = form.cleaned_data.get('start_time')
        if start_time and timezone.is_naive(start_time):
            form.instance.start_time = timezone.make_aware(start_time)

        # Mtumiaji aliyeunda (Organizer) ndiye mtumiaji aliyeingia sasa
        form.instance.organizer = self.request.user
        messages.success(self.request, "Mkutano umepangwa kwa mafanikio!")
        
        # Hifadhi kwanza ili tuweze kuongeza washiriki (attendees)
        response = super().form_valid(form)
        
        # Ongeza Organizer kama mshiriki wa mkutano pia
        self.object.attendees.add(self.request.user) 
        return response

class MeetingUpdateView(LeaderRequiredMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'content/meetings/meeting_form.html'
    success_url = reverse_lazy('meeting_list')
    
    def form_valid(self, form):
        # 1. Marekebisho ya Datetime: Fanya end_time iwe timezone-aware
        end_time = form.cleaned_data.get('end_time')
        
        if end_time and timezone.is_naive(end_time):
            # Badilisha end_time kuwa aware na iingize kwenye mfano (instance)
            form.instance.end_time = timezone.make_aware(end_time)

        # RUPIA KWA start_time (kama inahitajika/inaleta onyo)
        start_time = form.cleaned_data.get('start_time')
        if start_time and timezone.is_naive(start_time):
            form.instance.start_time = timezone.make_aware(start_time)
            
        messages.success(self.request, "Mkutano umerekebishwa!")
        return super().form_valid(form)
    
class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    model = Meeting
    template_name = 'content/meetings/meeting_confirm_delete.html'  # Badilisha jina la template kuwa sahihi
    success_url = reverse_lazy('meeting_list')
    
    # Optional: Ongeza check ya ruhusa kama inahitajika
    def get_queryset(self):
        queryset = super().get_queryset()
        # Ruhusu tu user anayemiliki au admin kufuta
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        # Ikiwa una field ya organizer kwenye Meeting
        return queryset.filter(organizer=self.request.user)    