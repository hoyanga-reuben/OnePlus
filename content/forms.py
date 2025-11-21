from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model
from .models import MembershipPayment, ANNUAL_FEE
from .models import Suggestion, Project
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal




User = get_user_model()


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


# ===================== Custom Signup Form =====================
class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=150, required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    profile_image = forms.ImageField(required=False, label="Profile Image")

    def save(self, request):
        user = super().save(request)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        user.save()
        return user


# ===================== Custom Login Form =====================
class CustomLoginForm(LoginForm):
    login = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")



# Kiwango cha chini cha malipo kwa awamu (1/4 ya Ada ya Mwaka)
# TZS 50,000 / 4 = TZS 12,500.00
MIN_INSTALLMENT_AMOUNT = ANNUAL_FEE / Decimal('4')

class PaymentForm(forms.ModelForm):
    # Kiasi sasa kinapokewa kama DecimalField ili kuwezesha malipo ya awamu
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Amount Paid (TZS)",
        required=True,
        # Weka kiwango cha chini kinachoonekana kwenye fomu
        min_value=MIN_INSTALLMENT_AMOUNT, 
        help_text=f"Weka kiasi unacholipa. Awamu ya chini kabisa ni TZS {MIN_INSTALLMENT_AMOUNT:,.2f}."
    )
    reference = forms.CharField(
        max_length=120,
        label="Transaction ID / Reference",
        required=True
    )
    date_paid = forms.DateField(
        label="Payment Date (Tarehe ulilipa)",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    proof = forms.FileField(
        label="Upload Payment Slip (Risiti)",
        required=False,
    )

    class Meta:
        model = MembershipPayment
        # Fields nyingine zote tutazipata moja kwa moja kwenye view
        fields = ['proof'] 

    def clean_date_paid(self):
        date_paid = self.cleaned_data.get('date_paid')
        if date_paid and date_paid > timezone.now().date():
            raise ValidationError("Tarehe ya malipo haiwezi kuwa ya baadae.")
        return date_paid
        
    def clean_amount(self):
        """
        Kuthibitisha kiasi cha malipo kiweze kufikia kiwango cha chini cha awamu 
        kilichowekwa (MIN_INSTALLMENT_AMOUNT).
        """
        amount = self.cleaned_data.get('amount')
        
        if amount and amount < MIN_INSTALLMENT_AMOUNT:
            # Hii inazuia member kulipa awamu ndogo sana, chini ya 1/4 ya ada.
            raise ValidationError(
                f"Kiasi cha chini kinachokubalika kwa awamu ni TZS {MIN_INSTALLMENT_AMOUNT:,.2f}."
            )
        
        if amount and amount <= 0:
            raise ValidationError("Kiasi cha malipo lazima kiwe chanya.")
            
        return amount
        
    def clean(self):
        # Validation nyingine zote zinaweza kuwekwa hapa
        return super().clean()
class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['subject','message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for your suggestion (e.g., App Feature Request)'
            }), 
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your suggestion or opinion here...'
            }),    
        }     



class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'start_date', 'end_date', 'hero_image']





# content/forms.py

from django import forms
from django.contrib.auth import get_user_model
from .models import Meeting, CustomUser # Hakikisha Meeting inapatikana

# ... (Forms zako nyingine hapa, kama SuggestionForm, PaymentForm n.k.) ...

class MeetingForm(forms.ModelForm):
    # Field ya Washiriki (attendees) itatumia MultipleChoice widget
    # Tunatumia CustomUser kama queryset
    attendees = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all().order_by('username'),
        widget=forms.CheckboxSelectMultiple, # Au forms.SelectMultiple
        required=False,
        label="Washiriki (Hiari)"
    )

    class Meta:
        model = Meeting
        fields = ['title', 'start_time', 'end_time', 'location', 'conference_link', 'description', 'attendees']
        widgets = {
            # Hii inahitaji HTML5 date/time input (zinafanya kazi vizuri kwenye browsers nyingi)
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'title': 'Kichwa cha Mkutano',
            'location': 'Mahali (Location/Venue)',
            'conference_link': 'Link ya Mkutano (Zoom/Meet/Jitsi URL)',
            'description': 'Maelezo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inahakikisha mtindo wa datetime unapatana na widget
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']
        # Unaweza kuondoa organizer kutoka kwa attendees list ili asijichague mwenyewe
        if 'initial' in kwargs and 'organizer' in kwargs['initial']:
             self.fields['attendees'].queryset = CustomUser.objects.exclude(pk=kwargs['initial']['organizer'].pk).order_by('username')