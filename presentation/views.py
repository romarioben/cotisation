from django.shortcuts import render
from . import forms
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import threading


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


# Create your views here.
def home(request):
    #Il n'y a pas de base html dans ce cas, le base est aussi le home
    if request.method == "POST":
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            email_subject = "Vous envoyez une requête sur GesPres"
            email = contact_message.email
            message1 = render_to_string('presentation/email_contact.html',
                {
                    'objet': contact_message.objet,
                    'nom_et_prenom': contact_message.nom,
                }
            )

            email_message1 = EmailMessage(
                email_subject,
                message1,
                settings.EMAIL_HOST_USER,
                [email]
            )
            
            message2 = render_to_string('presentation/email_contact_to_romario.html',
                {
                    'objet': contact_message.objet,
                    'email': contact_message.email,
                    'message': contact_message.message,
                    'nom_et_prenom': contact_message.nom,
                }
            )
            email_message2 = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                ["romariobenisto@gmail.com"]
            )

            EmailThread(email_message1).start()
            EmailThread(email_message2).start()
            form = forms.ContactForm()
            return render(request, 'presentation/base.html', locals())
        return render(request, 'presentation/base.html', locals())
            
    form = forms.ContactForm()
    return render(request, "presentation/base.html", locals())