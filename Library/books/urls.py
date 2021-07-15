from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from . import views
from rest_framework_swagger.views import get_swagger_view
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('register',views.RegisterNewView , basename='register')


urlpatterns = [
    path('test',views.test),
    path('roles',views.RoleView.as_view(),name='role'),
    path('role/<int:id>',views.RoleEditView.as_view(),name='edit-role'),
    # path('signup',views.RegisterView.as_view(),name='signup'),
    path('login',views.LoginView.as_view(),name='login'),
    path('logout',views.LogoutView.as_view(),name='logout'),
    path('user/<int:id>',views.EditUserView.as_view(),name='user_edit'),
    path('authors',views.AuthorView.as_view(),name='author'),
    path('author/<int:id>',views.AuthorEditView.as_view(),name='author_edit'),
    path('genres',views.GenreView.as_view(),name='genres'),
    path('genre/<int:id>',views.GenreEditView.as_view(),name='genre_edit'),
    path('books',views.BookView.as_view(),name='books'),
    path('book/<int:id>',views.BookEditView.as_view(),name='book_edit'),
    path('book/authors',views.BookSearchByAuthor.as_view(),name='book_author'),
    path('book/genres',views.BookSearchByGenre.as_view(),name='book_genre'),
    path('book/request-type',views.BookRequestTypeView.as_view(),name='book_request_type'),
    path('book/request-type/<int:id>',views.BookRequestTypeEditView.as_view(),name='book_request_type'),
    path('available-books',views.AvailableBookView.as_view(),name='available_books'),
    path('book/requests',views.BookRequestView.as_view(),name='book_requests'),
    path('book/request/<int:id>',views.BookRequestAddEditView.as_view(),name='book_requests'),
    path('issued-books',views.IssuedBookView.as_view(),name='issued_books'),
    path('return-book',views.ReturnBookView.as_view(),name='return_book'),
    path('lost-book',views.LostBookView.as_view(),name='lost_book'),
    path('viewset/',include(router.urls)),
    
]