from django.contrib import admin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','issued_book']

admin.site.register(CustomUser,CustomUserAdmin)