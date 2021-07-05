from django.db import models
from django.db.models import fields,Q
from django.db.models.base import Model
from rest_framework import serializers
from .models import Role, CustomUser, Author, Genre, Book, Book_issue
from rest_framework.validators import UniqueValidator
from datetime import date, datetime
from django.contrib.auth.hashers import make_password
from collections import OrderedDict

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

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

class RegisterMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    type = serializers.PrimaryKeyRelatedField(required=True,queryset=Role.objects.filter(~Q(name='Librarian')))

    class Meta:
        model = CustomUser
        fields = ('id','username', 'password', 'confirm_password', 'email','type')

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

class EditUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True,required=False,style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username','password','confirm_password','email',)
        read_only_fields = ('password',)
           
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'password']
    
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('__all__')

# for display genre names only in book
class GenreBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name',)

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    genre_type = GenreBookSerializer(source='genre',read_only=True, many=True)

    class Meta:
        model = Book
        fields = ('id','title','author','author_name','genre','genre_type','is_issued',)
        read_only_fields = ('is_issued',)
        extra_kwargs = {
            'author': {'write_only': True},
            'genre': {'write_only': True},
        }

class BookSearchByAuthorSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(required=True,queryset=Author.objects.all())
    class Meta:
        model = Book
        fields = ('name',)

class BookSearchByGenreSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(required=True,many=True,queryset=Genre.objects.all())
    class Meta:
        model = Book
        fields = ('name',)

class GetBookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    genre_type = GenreBookSerializer(source='genre',read_only=True, many=True)
    issue_date = serializers.DateTimeField(default=datetime.now(),write_only=True,)
    return_date = serializers.DateTimeField(write_only=True, required=True,)

    class Meta:
        model = Book
        fields = ('title','author_name','genre_type','issue_date','return_date',)
        
class BookIssueSerializer(serializers.ModelSerializer):
    book_name = serializers.ReadOnlyField(source='book.title')
    user_name = serializers.ReadOnlyField(source='user.username',read_only=True)
    return_book_name = serializers.CharField(write_only=True)

    class Meta:
        model = Book_issue
        fields = ('book_name','date_issue','date_return','user_name','is_return','charge','return_book_name',)
        read_only_fields = ('date_issue','date_return','charge','is_return')
