from django.http.response import JsonResponse
from django.shortcuts import render
from django.http.response import JsonResponse,HttpResponse
from rest_framework import permissions, serializers
from .serializers import BookIssueSerializer, GetBookSerializer,RoleSerializer, RegisterSerializer, RegisterMemberSerializer, EditUserSerializer, LoginSerializer, AuthorSerializer,GenreSerializer, BookSerializer, BookSearchByAuthorSerializer, BookSearchByGenreSerializer
from rest_framework import generics
from .models import CustomUser,Author,Genre, Book, Role, Book_issue
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
from rest_framework.permissions import BasePermission , AllowAny,IsAdminUser,IsAuthenticated, SAFE_METHODS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from datetime import date,datetime
from rest_framework import viewsets
from django.db.models import Q
import csv


# Create your views here.


"""
    Permission
"""


class IsLibrarian(BasePermission):
    def has_permission(self,request,view):
        if request.user.is_authenticated:
            current_user = request.user
            if current_user.type.name == 'Librarian':
                return True
            return False
        return False

class IsMember(BasePermission):
    def has_permission(self,request,view):
        if request.user.is_authenticated:
            current_user = request.user
            if current_user.type.name == 'Member':
                return True
            return False
        return False

class IsAnonymous(BasePermission):
    message = "User is already logged in."
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return True
        return False
        

"""
    API starts from here
"""
def test(request):
    return JsonResponse({'test':'OK'})

class RoleView(APIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser|IsLibrarian]

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles,many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer= RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'meesage':'Data added Successfully.'},status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)          
 
class RegisterView(APIView):
    
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser|IsLibrarian]

    def get_serializer_class(self):
        if self.request.user.is_staff == True:
            return RegisterSerializer
        return RegisterMemberSerializer
    
    def get(self,request):
        if request.user.is_staff:
            user = CustomUser.objects.filter(is_superuser=False)
        else:
            user = CustomUser.objects.filter(type__name='Member')
        serializer = RegisterSerializer(user,many=True)
        return Response(serializer.data)
        
    def post(self,request):
        if request.user.is_staff:
            serializer= RegisterSerializer(data=request.data)
        else:
            serializer= RegisterMemberSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
class RegisterNewView(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser|IsLibrarian]

    def get_queryset(self):
        user = CustomUser.objects.all()
        return user

    def get_serializer_class(self):
        if self.request.user.is_staff == True:
            return RegisterSerializer
        return RegisterMemberSerializer

    def list(self, request):
        if request.user.is_staff:
            user = CustomUser.objects.filter(is_superuser=False)
        else:
            user = CustomUser.objects.filter(~Q(type__name='Librarian'),is_superuser=False )
        serializer = RegisterSerializer(user,many=True)
        return Response(serializer.data)

    def create(self,request):
        if request.user.is_staff:
            serializer= RegisterSerializer(data=request.data)
        else:
            serializer= RegisterMemberSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    serializer_class = LoginSerializer
    
    permission_classes = [IsAnonymous]

    def post(self, request):
        if request.user.is_anonymous:
            serializer= LoginSerializer(data=request.data)

            if serializer.is_valid():
                user = authenticate(request,username=request.data['username'],password=request.data['password'])

                if user is not None:
                    login(request,user)
                    return Response({'data':'Login Successfully.'},status=status.HTTP_202_ACCEPTED)
                
                return Response({'error':'Invalid Username!!!'},status=status.HTTP_401_UNAUTHORIZED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error':'Already Logged In...'},status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):
        logout(request)
        return Response({'data':'logout Successfully..'},status=status.HTTP_200_OK)

class EditUserView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = EditUserSerializer

    def get_object(self,id,type):
        try:
            user = CustomUser.objects.get(id=id)
            if type == 'Librarian':
                try:
                    if user.type.name != "Member":
                        return None

                except:
                    return None

            return user

        except CustomUser.DoesNotExist:
            return None

    def get(self,request,id):
        type_name = str(request.user.type)
        user = self.get_object(id,type_name)
        if user:
            serializer = EditUserSerializer(user)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        type_name = str(request.user.type)
        user = self.get_object(id,type_name)
        if user:

            if "confirm_password" in request.data:
                if self.request.data['confirm_password'] != "":
                    user.password = make_password(request.data['confirm_password'])

            if "email" in request.data:
                if self.request.data['email'] != "":
                    user.email = request.data['email']

            if "username" in request.data:
                if self.request.data['username'] != "":
                    user.email = request.data['email']

            user.save()
            return Response(request.data,status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        type_name = str(request.user.type)
        user = self.get_object(id,type_name)
        if user:
            user.delete()
            return Response(status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

class AuthorView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = AuthorSerializer

    def get(self,request):
        author = Author.objects.all()
        serializer = AuthorSerializer(author,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = AuthorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class AuthorEditView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = AuthorSerializer

    def get_object(self,id):
        try:
            author = Author.objects.get(id=id)
            return author

        except Author.DoesNotExist:
            return None
            
    def get(self,request,id):
        author = self.get_object(id)
        if author:
            serializer = AuthorSerializer(author)
            return Response(serializer.data)

        return Response({'error':'No data Found'})

    def put(self,request,id):
        author = self.get_object(id)
        if author:
            serializer = AuthorSerializer(author,data=request.data) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No data Found'})

    def delete(self,request,id):
        author = self.get_object(id)
        if author:
            author.delete()
            return Response(status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'})

class GenreView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = GenreSerializer

    def get(self,request):
        genre = Genre.objects.all()
        serializer = GenreSerializer(genre,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = GenreSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class GenreEditView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = GenreSerializer

    def get_object(self,id):
        try:
            genre = Genre.objects.get(id=id)
            return genre

        except Genre.DoesNotExist:
            return None

    def get(self,request,id):
        genre = self.get_object(id)
        if genre:
            serializer = GenreSerializer(genre)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        genre = self.get_object(id)
        if genre:
            serializer = GenreSerializer(genre,data=request.data) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        genre = self.get_object(id)
        if genre:
            genre.delete()
            return Response(status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

class BookView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = BookSerializer

    def get(self,request):
        books = Book.objects.all()
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class BookEditView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = BookSerializer

    def get_object(self,id):
        try:
            book = Book.objects.get(id=id)
            return book

        except Book.DoesNotExist:
            return None

    def get(self,request,id):
        book = self.get_object(id)
        if book:
            serializer = BookSerializer(book)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        book = self.get_object(id)
        if book:
            serializer = BookSerializer(book,data=request.data) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        book = self.get_object(id)
        if book:
            book.delete()
            return Response({'detail':'Book is deleted'},status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

class BookSearchByAuthor(APIView):
    permission_classes = [IsAdminUser|IsLibrarian|IsMember]
    serializer_class = BookSearchByAuthorSerializer

    def get_object(self,author):
        try:
            books = Book.objects.filter(author=author)
            return books

        except Book.DoesNotExist:
            return None

    def post(self,request):
        books = self.get_object(request.data['name'])

        if books:
            serializer = BookSerializer(books,many=True)
            return Response(serializer.data)

        return Response({'details':'No data found'},status=status.HTTP_404_NOT_FOUND)

class BookSearchByGenre(APIView):
    permission_classes = [IsAdminUser|IsLibrarian|IsMember]
    serializer_class = BookSearchByGenreSerializer

    def get_object(self,genre):
        try:
            books = Book.objects.filter(genre=genre)
            return books

        except Book.DoesNotExist:
            return None

    def post(self,request):
        books = self.get_object(request.data['name'])

        if books:
            serializer = BookSerializer(books,many=True)
            return Response(serializer.data)

        return Response({'details':'No data found'},status=status.HTTP_404_NOT_FOUND)

class AvailableBookView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian|IsMember]
    serializer_class = GetBookSerializer

    def get(self,request):
        books = Book.objects.filter(is_issued=False)
        serializer = GetBookSerializer(books,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        serializer =GetBookSerializer(data=request.data)
        if serializer.is_valid():
            
            user = request.user
            try:
                book = Book.objects.get(title=request.data['title'])
                if user.issued_book < 2:
                    user.issued_book +=1
                    user.save()
                    book.is_issued = True
                    book.save()
                    book_issued= Book_issue(book=book,date_issue=request.data['issue_date'],
                        date_return = request.data['return_date'],user=user
                    )
                    book_issued.save()
                    return Response({'msg':'success'},status=status.HTTP_202_ACCEPTED)

                return Response({'error':'Already reach maximum number of isseud book.Please return issued book and try again'},status=status.HTTP_412_PRECONDITION_FAILED)

            except Exception as e:
                print(e)
                return Response({'error':'Book not available'},status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class IssuedBookView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    
    # def get(self,request):
    #     books = Book_issue.objects.all()
    #     serializer = BookIssueSerializer(books,many=True)
    #     return Response(serializer.data)

    def get(self, request):
        books = Book_issue.objects.all()
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Book Title','Book Author','Member Name','Date Of Issue','Date of Return','is_return'])
        if books:
            for book in books.values_list('book__title','book__author__name','user__username','date_issue','date_return','is_return'):
                writer.writerow(book)
            response['Content-Disposition'] = 'attachment; filename="book_issued.csv"'
            return response
        else:
            return Response({'details':'No Data Found'},status=status.HTTP_404_NOT_FOUND)

class ReturnBookView(APIView):
    permission_classes = [IsMember]
    serializer_class = BookIssueSerializer

    def get_object(self,book,user):
        try:
            user = CustomUser.objects.get(id=id)
            if type == 'Librarian':
                try:
                    if user.type.name != "Member":
                        return None

                except:
                    return None

            return user

        except CustomUser.DoesNotExist:
            return None

    def get(self,request):
        books = Book_issue.objects.filter(user=request.user,is_return=False)
        today = date.today()
        if books:
            for data in books:
                price = (today-data.date_return.date())
                if price.days > 0:
                    charge = 10 * price.days
                    data.charge = charge
                    data.save()

            serializers = BookIssueSerializer(books,many=True)
            return Response(serializers.data)

        return Response({'detail':'There are no issue book.'},status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = CustomUser.objects.get(username=request.user.username)
        book = Book.objects.get(title=request.data['return_book_name'])
        try:
            book_user_check = Book_issue.objects.get(book=book,user=request.user,is_return=False)
            book_user_check.is_return = True
            user.issued_book -= 1
            user.save()
            book.is_issued = False
            book.save()
            book_user_check.date_return = datetime.now()
            book_user_check.save()
            return Response({'msg':'Book return successfully.'},status=status.HTTP_202_ACCEPTED)

        except:
            return Response({'error':'Book not Found.'},status=status.HTTP_404_NOT_FOUND)
            