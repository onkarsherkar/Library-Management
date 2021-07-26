from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

# Maintain user 
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
    # is_issued = models.BooleanField(default=False)
    price = models.FloatField()
    # no_copy = models.IntegerField()
    

    def __str__(self):
        return self.title

class Unique_identifier(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    unique_no = models.CharField(max_length=10,validators=[MinLengthValidator(10)],unique=True)
    is_issue = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    def __str__(self):
        return self.unique_no

class Book_request_type(models.Model):
    request_name = models.CharField(max_length=100)

    def __str__(self):
        return self.request_name

# Maintain current request only
class Book_request(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    date_issue = models.DateField()
    date_return = models.DateField()
    return_lost_request_date = models.DateField(null=True) # Only for return request and Lost request
    user = models.ForeignKey(CustomUser,on_delete=CASCADE)
    type = models.ForeignKey(Book_request_type,on_delete=CASCADE)
    charge = models.IntegerField(default=0)

# Maintain request 
class Book_request_log(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    unique_id = models.ForeignKey(Unique_identifier,on_delete=models.CASCADE,null=True)
    date_issue = models.DateField()
    expected_date_return = models.DateField()
    actual_date_return = models.DateField(null=True)
    user = models.ForeignKey(CustomUser,on_delete=CASCADE)
    type = models.ForeignKey(Book_request_type,on_delete=CASCADE)
    charge = models.IntegerField(default=0)

