from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField

    class Meta():
        model = User
        fields = ['username','email','password1','password2']



class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'}))


from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extracting form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send the email
            send_mail(
                subject=f"Inquiry from {name}",
                message=f"Message from {name} ({email}):\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,  # Use your verified email
                recipient_list=['zyadwael2009@gmail.com'],  # Replace with your email
                fail_silently=False,
            )

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

