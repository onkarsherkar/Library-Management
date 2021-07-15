from django.db import models
from django.db.models import fields,Q
from django.db.models.base import Model
from rest_framework import serializers
from rest_framework import validators
from .models import Book_request, Role, CustomUser, Author, Genre, Book, Book_request_log,Book_request_type
from rest_framework.validators import UniqueValidator
from datetime import date, datetime
from django.contrib.auth.hashers import make_password
from collections import OrderedDict

# serializer for Role 
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# Serailizer for Librarain User
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    type_name = serializers.ReadOnlyField(source='type.name')

    class Meta:
        model = CustomUser
        fields = ('id','username', 'password', 'confirm_password', 'email','type','type_name',)
        extra_kwargs = {
            'type': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"error": "Password fields didn't match."})

        if attrs['type'] is None:
            raise serializers.ValidationError({"error":"type field required"})

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            type=validated_data['type']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

# Serailizer for Memeber User
class RegisterMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    type = serializers.PrimaryKeyRelatedField(required=True,queryset=Role.objects.filter(~Q(name='Librarian')))
    type_name = serializers.ReadOnlyField(source='type.name')
    class Meta:
        model = CustomUser
        fields = ('id','username', 'password', 'confirm_password', 'email','type','type_name')
        extra_kwargs = {
            'type': {'write_only': True},
        }
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"error": "Password fields didn't match."})

        if attrs['type'] is None:
            raise serializers.ValidationError({"error":"type field required"})

        return attrs

        


    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            type=validated_data['type']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

# serializer for edit exisiting user
class EditUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True,required=False,style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username','password','confirm_password','email',)
        read_only_fields = ('password',)
           
# Login Serializer           
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'password']
 
# Author Serializer    
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

# Genre Serializer
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('__all__')

# for display genre  names only in book
class GenreBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name',)

# Book Serializer
class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    genre_type = GenreBookSerializer(source='genre',read_only=True, many=True)

    class Meta:
        model = Book
        fields = ('id','title','author','author_name','genre','genre_type','is_issued','no_copy','price')
        read_only_fields = ('is_issued',)
        extra_kwargs = {
            'author': {'write_only': True},
            'genre': {'write_only': True},
        }

# Book Search by author
class BookSearchByAuthorSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(required=True,queryset=Author.objects.all())
    class Meta:
        model = Book
        fields = ('name',)

# Book search by genre
class BookSearchByGenreSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(required=True,many=True,queryset=Genre.objects.all())
    class Meta:
        model = Book
        fields = ('name',)

# Display Books 
class GetBookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    genre_type = GenreBookSerializer(source='genre',read_only=True, many=True)
    issue_date = serializers.DateField(default=datetime.now(),write_only=True,)
    return_date = serializers.DateField(write_only=True, required=True,)
    #type = serializers.PrimaryKeyRelatedField(write_only=True,required=True,queryset=Book_request_type.objects.all())
    class Meta:
        model = Book
        fields = ('title','author_name','genre_type','issue_date','return_date',)

# Book request serializer for add new request name
class BookRequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book_request_type
        fields = ('id','request_name',)

# Book Request serializer for display exisiting and new new request
class BookRequestSerializer(serializers.ModelSerializer):
    book_name = serializers.ReadOnlyField(source='book.title')
    user_name = serializers.ReadOnlyField(source='user.username',read_only=True)
    request_type = serializers.ReadOnlyField(source='type.request_name',read_only=True)
    user = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CustomUser.objects.filter(~Q(type=None)))
    class Meta:
        model = Book_request
        fields = ('id','book_name','book','date_issue','date_return','return_lost_request_date','user_name','user','request_type','type','charge')
        read_only_fields = ('date_issue','date_return','return_lost_request_date')
        extra_kwargs = {
            'book': {'write_only': True},
            'user': {'write_only': True},
            'type': {'write_only': True}
        }

# Add, Delete serializer request
class BookRequestAddEditSerializer(serializers.ModelSerializer):
    book_name = serializers.ReadOnlyField(source='book.title')
    user_name = serializers.ReadOnlyField(source='user.username',read_only=True)
    request_type = serializers.ReadOnlyField(source='type.request_name',read_only=True)
    user = serializers.PrimaryKeyRelatedField(write_only=True,queryset=CustomUser.objects.filter(~Q(type=None)))
    

    class Meta:
        model = Book_request
        fields = ('id','book_name','book','date_issue','date_return','user_name','user','request_type','type')
        extra_kwargs = {
            'book': {'write_only': True},
            'user': {'write_only': True},
            'type': {'write_only': True}
        }

# Return, Lost, Issue Book Request serializer
class BookIssueSerializer(serializers.ModelSerializer):
    book_name = serializers.ReadOnlyField(source='book.title')
    user_name = serializers.ReadOnlyField(source='user.username',read_only=True)
    return_book_name = serializers.CharField(write_only=True)

    class Meta:
        model = Book_request_log
        fields = ('book_name','date_issue','expected_date_return','user_name','charge','return_book_name',)
        read_only_fields = ('date_issue','expected_date_return','charge')
