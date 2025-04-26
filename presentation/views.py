from django.shortcuts import render

# Create your views here.
def home(request):
    #Il n'y a pas de base html dans ce cas, le base est aussi le home
    return render(request, "presentation/base.html", locals())