from django.shortcuts import render, get_object_or_404, redirect, HttpResponse

from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from . import models#, forms, autresfonctions, report
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import  Q
# import html
# from bs4 import BeautifulSoup
import unidecode
from django.utils.timezone import now
import pandas as pd
import numpy as np
from django.core.paginator import Paginator
from auth_app.forms import SignupForm
from . import forms
# Create your views here.

@login_required
def app_home(request):
    page_name = "Dashboard"
    return render(request, "app/home.html", locals())

def registration(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        form1 = forms.GroupeForm(request.POST)
        if form.is_valid() and form1.is_valid():
            user = form.save()
            groupe = form1.save()
        else:
            return render(request, 'app/registration.html', locals())
        user.groupe = groupe
        user.save()
        return redirect('login')
    else:
        form = SignupForm()
        form1 = forms.GroupeForm()
        return render(request, 'app/registration.html', locals())


def membre(request):
    page_name = "Membres"
    return render(request, "app/membre.html", locals())