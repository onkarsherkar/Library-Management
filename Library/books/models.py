from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    issued_book = models.IntegerField(default=0, validators=[
        MinValueValidator(0), MaxValueValidator(2)
    ])
    type = models.ForeignKey(Role,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.username

class Author(models.Model):
    name = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100,unique=True)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    is_issued = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Book_issue(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    date_issue = models.DateTimeField()
    date_return = models.DateTimeField()
    user = models.ForeignKey(CustomUser,on_delete=CASCADE)
    is_return = models.BooleanField(default=False)
    charge = models.IntegerField(default=0)

