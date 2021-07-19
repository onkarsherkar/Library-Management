from django.http import response
from django.test import TestCase
import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import CustomUser, Role, Author, Genre

class SampleTestcase(APITestCase):
    def test_sample(self):
        response = self.client.get('/test')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

# For admin Test case (can add labrian test case also)

class AddRoleTestcase(APITestCase):
    list_url = reverse("role")

    def setUp(self):
        CustomUser.objects.create_superuser('admin','admin@gmail.com','root')
        self.client.login(username='admin',password='root')

    # get
    def test_display_role(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    # post
    def test_add_role(self):
        data = {
            'name':'Librarian'
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
    
class EditRoleTestcase(APITestCase):
    list_url = reverse("edit-role",kwargs={'id':1})
    
    def setUp(self) -> None:
        CustomUser.objects.create_superuser('admin','admin@gmail.com','root')
        self.client.login(username='admin',password='root')
        Role.objects.create(name='Labrarian')

    # get
    def test_display_role(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_302_FOUND)

    # put
    def test_edit_role(self):
        data = {
            'name':'abc'
        }
        response = self.client.put(self.list_url,data)
        self.assertEqual(response.status_code,status.HTTP_202_ACCEPTED)

    def test_delete_role(self):
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_202_ACCEPTED)

class AddUserTestcase(APITestCase):
    # list_url = reverse("register")

    def setUp(self):
        CustomUser.objects.create_superuser('admin','admin@gmail.com','root')
        self.client.login(username='admin',password='root')
        Role.objects.create(name='Labrarian')

    # post
    def test_add_user(self):
        data = {
            'username':'Tom',
            'password':'qwe',
            'confirm_password':'qwe',
            'email':'tom@gmail.com',
            'type':1
        }
        response = self.client.post('/viewset/register/',data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    # get
    def test_display_user(self):
        response = self.client.get('/viewset/register/')
        self.assertEqual(response.status_code,status.HTTP_302_FOUND)

class LoginTestcase(APITestCase):
    list_url = reverse("login")

    def setUp(self) -> None:
        CustomUser.objects.create_superuser('admin','admin@gmail.com','root')
    # post
    def test_login(self):
        data ={
            'username':'admin',
            'password':'root'
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code,status.HTTP_202_ACCEPTED)

class LogoutTestcase(APITestCase):
    list_url = reverse("logout")

    def setUp(self) -> None:
        CustomUser.objects.create_superuser('admin','admin@gmail.com','root')
        self.client.login(username='admin',password='root')
    # post
    def test_logout(self):
        response = self.client.post(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_202_ACCEPTED)

class AddAuthorTestcase(APITestCase):       
    list_url = reverse("author")

    def setUp(self):
        Role.objects.create(name='Librarian')
        role=Role.objects.get(id=1)
        CustomUser.objects.create_user(username='Tom',email='tom@gmail.com',password='qwe',type=role)
        self.client.login(username='Tom',password='qwe')
    
    # post
    def test_add_author(self):
        data = {
            'name':'Naryan K',
            'address':'UK'
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    # get
    def test_display_auhtor(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_302_FOUND)

class AddBookTestcase(APITestCase):
    list_url = reverse("books")

    def setUp(self):
        role=Role.objects.create(name='Librarian')
        CustomUser.objects.create_user(username='Tom',email='tom@gmail.com',password='qwe',type=role)
        self.client.login(username='Tom',password='qwe')
        Author.objects.create(name='abc',address='xyz')
        Genre.objects.create(name='fiction')
        Genre.objects.create(name='novel')
        
    # post
    def test_add_book(self):
        data = {
            'title':'Naryan K',
            'author':1,
            'genre':[1,2],
            'price':1000,
            'no_copy':5
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    # get
    def test_display_auhtor(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_302_FOUND)