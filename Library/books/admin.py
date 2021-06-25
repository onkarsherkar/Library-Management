from django.contrib import admin
from .models import CustomUser,Author,Genre

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username','email','issued_book']

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id','name','address']

class GenreAdmin(admin.ModelAdmin):
    list_display = ['id','name']

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Author,AuthorAdmin)
admin.site.register(Genre,GenreAdmin)