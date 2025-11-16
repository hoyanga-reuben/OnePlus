from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model
from .models import MembershipPayment
from .models import Suggestion


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



class PaymentForm(forms.ModelForm):
    class Meta:
        model = MembershipPayment
        fields = ['proof', 'payment_method']  # remove amount field!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: make fields clearer
        self.fields['proof'].label = "Upload Payment Slip"
        self.fields['payment_method'].widget = forms.Select(
            choices=[('bank_transfer', 'CRDB Bank Transfer')]
        )

from django import forms
from .models import Suggestion

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your suggestion or opinion here...'
            }),
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your suggestion or opinion here...'
            }),
        }



# content/forms.py
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'start_date', 'end_date', 'hero_image']
