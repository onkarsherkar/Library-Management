from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.base import Model
from django.db.models.deletion import CASCADE

# Create your models here.

class CustomUser(AbstractUser):
    issued_book = models.IntegerField(default=0, validators=[
        MinValueValidator(0), MaxValueValidator(2)
    ])


class Author(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

class Genre(models.Model):
    name = models.CharField(max_length=100)

class Books(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    is_issued = models.BooleanField(default=False)

class Book_issue(models.Model):
    book = models.ForeignKey(Books,on_delete=models.CASCADE)
    date_issue = models.DateTimeField()
    date_return = models.DateTimeField()
    user = models.ForeignKey(CustomUser,on_delete=CASCADE)

class Book_return(models.Model):
    book = models.ForeignKey(Books,on_delete=models.CASCADE)
    date_return = models.DateTimeField()
    user = models.ForeignKey(CustomUser,on_delete=CASCADE)
    charge = models.IntegerField()
    