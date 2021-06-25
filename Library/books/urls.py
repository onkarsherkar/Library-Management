
from django.urls import path
from . import views
urlpatterns = [
    path('test',views.test),
    path('signup',views.RegisterView.as_view(),name='signup'),
    path('login',views.LoginView.as_view(),name='login'),
    path('logout',views.LogoutView.as_view(),name='logout')
    
]