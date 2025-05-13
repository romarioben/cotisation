from django.contrib import admin

from . import models

# Register your models here.

@admin.register(models.Contact)
class ContactModelAdmin(admin.ModelAdmin):
    list_display = ['id','nom', "email", "objet", "message"]