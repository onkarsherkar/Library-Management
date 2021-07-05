from django.contrib import admin
from .models import Book, CustomUser,Author,Genre, Role,Book_issue

# Register your models here.

class RoleAdmin(admin.ModelAdmin):
    list_display = ['id','name']

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username','email','issued_book']

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id','name','address']

class GenreAdmin(admin.ModelAdmin):
    list_display = ['id','name']

class role_inline(admin.TabularInline):
    model = Book
    extra = 1

class BooksAdmin(admin.ModelAdmin):
    list_display = ('id','title','author','is_issued',)

class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('id','book','date_issue','date_return','user','charge','is_return')

admin.site.register(Role,RoleAdmin)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Author,AuthorAdmin)
admin.site.register(Genre,GenreAdmin)
admin.site.register(Book,BooksAdmin)
admin.site.register(Book_issue,BookIssueAdmin)