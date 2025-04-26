from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.contrib.auth.decorators import login_required
from . import forms, models
from django.views import View
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,  DjangoUnicodeDecodeError, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

import threading


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


# Create your views here.

class MyLoginView(LoginView):
    form_class = forms.LoginForm
    template_name = 'auth_app/login.html'
    pass

class MyLogoutView(LogoutView):
    pass

class MyPasswordChangeView(PasswordChangeView):
       pass

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    pass


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth_app/password_change_complete.html'
    pass


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = forms.MySetPasswordForm
    template_name = 'auth_app/password_change.html'
    pass


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth_app/password_reset_done.html'
    pass

class MyPasswordResetView(PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'auth_app/password_reset.html'
    pass

class MyRegistrationView(View):
    def get(self, request):
        form = forms.SignupForm()
        print(form)
        return render(request, "auth_app/registration.html", locals())
    
    def post(self, request):
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        else:
            return render(request, "auth_app/registration.html", locals())
        
        

@login_required
def home(request):
    return render(request, "auth_app/home.html", locals())

@login_required
def verify_email_send(request):
    user = request.user
    if request.user.email:
        email = request.user.email
    else:
        return redirect("home")
    current_site = get_current_site(request)
    email_subject = 'Verifiez votre adresse email'
    message = render_to_string('auth_app/verify_email.html',
        {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        }
    )

    email_message = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [email]
    )

    EmailThread(email_message).start()
    #messages.add_message(request, messages.SUCCESS, 'account created succesfully')


    return render(request, "auth_app/verify_email_done.html", locals())

def verify_email(request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            messages.add_message(request, messages.SUCCESS, 'email verified successfully')
            return render(request, "auth_app/verify_email_complete.html")
        return render(request, 'auth/email_verify_failed.html', status=401)

