from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['id','username', 'role', 'groupe']
