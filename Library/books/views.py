from enum import unique
from django.db.models.fields import DateTimeField
from django.http.response import JsonResponse
from django.shortcuts import render
from django.http.response import JsonResponse,HttpResponse
from rest_framework import permissions, serializers
from .serializers import BookIssueSerializer,UniqeIdentifierSerializer, UniqeIdentifierEditSerializer,BookRequestSerializer, GetBookSerializer,RoleSerializer, RegisterSerializer, RegisterMemberSerializer, EditUserSerializer, LoginSerializer, AuthorSerializer,GenreSerializer, BookSerializer, BookSearchByAuthorSerializer, BookSearchByGenreSerializer, BookRequestTypeSerializer,\
BookRequestAddEditSerializer
from rest_framework import generics
from .models import Book_request, CustomUser,Author,Genre, Book, Role, Book_request_log, Book_request_type, Unique_identifier
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
from django.utils import timezone
import pytz


# Create your views here.


"""
    Permission
"""


class IsLibrarian(BasePermission):
    def has_permission(self,request,view):
        if request.user.is_authenticated:
            current_user = request.user
            try:
                if current_user.type.name == 'Librarian':
                    return True
                return False
            except:
                return False
        return False

class IsMember(BasePermission):
    def has_permission(self,request,view):
        if request.user.is_authenticated:
            current_user = request.user
            try:
                if current_user.type.name == 'Member':
                    return True
                return False
            except:
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

# Test api
def test(request):
    return JsonResponse({'test':'OK'})

#  Creat and display system role (Librarian,Member)
class RoleView(APIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser|IsLibrarian]

    def get(self, request):
        type_name = str(request.user.type)
        if type_name == 'Librarian':
            roles = Role.objects.filter(~Q(name='Librarian'))
        else:
            roles = Role.objects.all()
        serializer = RoleSerializer(roles,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request):
        serializer= RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'meesage':'Data added Successfully.'},status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)          
 
# Modify Delete exisiting role 
class RoleEditView(APIView):
    
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser|IsLibrarian]

    def get_object(self,id,type_name):
        try:
            role = Role.objects.get(id=id)
            if type_name == 'Librarian' and role.name == "Librarian":
                return 'Not access'
            return role

        except:
            return None

    def get(self,request,id):
        type_name = str(request.user.type)
        role = self.get_object(id,type_name)

        if role == 'Not access':
            return Response({'error':'You do not have access'},status=status.HTTP_401_UNAUTHORIZED)

        if role:
            serializer = RoleSerializer(role)
            return Response(serializer.data,status=status.HTTP_302_FOUND)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        type_name = str(request.user.type)
        role = self.get_object(id,type_name)

        if role == 'Not access':
            return Response({'error':'You do not have access'},status=status.HTTP_401_UNAUTHORIZED)

        if role:
            if "name" in request.data:
                if self.request.data['name'] != "":
                    role.name = request.data['name']
                    role.save()
                    return Response(request.data,status=status.HTTP_202_ACCEPTED)

                return Response({'error':'Field is empty'},status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        type_name = str(request.user.type)
        role = self.get_object(id,type_name)

        if role == 'Not access':
            return Response({'error':'You do not have access'},status=status.HTTP_401_UNAUTHORIZED)

        if role:
            role.delete()
            return Response(request.data,status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)


# Display exisiting user and register new user
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
        return Response(serializer.data,status=status.HTTP_302_FOUND)

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
        return Response({'data':'logout Successfully..'},status=status.HTTP_202_ACCEPTED)

# Modify, Delete exisiting user
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

# Add book Auther
class AuthorView(APIView):
    permission_classes = [IsLibrarian|IsAdminUser]
    serializer_class = AuthorSerializer

    def get(self,request):
        author = Author.objects.all()
        serializer = AuthorSerializer(author,many=True)
        return Response(serializer.data,status=status.HTTP_302_FOUND)

    def post(self,request):
        serializer = AuthorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Modify,Delete exisiting author
class AuthorEditView(APIView):
    permission_classes = [IsLibrarian]
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

# Add diffrent genre
class GenreView(APIView):
    permission_classes = [IsLibrarian]
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

# Modify,Delete genre
class GenreEditView(APIView):
    permission_classes = [IsLibrarian]
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

# Add new Books
class BookView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian]
    serializer_class = BookSerializer

    def get(self,request):
        books = Book.objects.all()
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data,status=status.HTTP_302_FOUND)

    def post(self,request):
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Add unique Identifier
class UniqueIdentifierView(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = UniqeIdentifierSerializer

    def get(self,request):
        unique_identifier = Unique_identifier.objects.all()
        serializer = UniqeIdentifierSerializer(unique_identifier,many=True)
        return Response(serializer.data,status=status.HTTP_302_FOUND)

    def post(self,request):
        serializer = UniqeIdentifierSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Edit unique Identifier
class EditUniqueIdentifier(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = UniqeIdentifierEditSerializer

    def get_object(self,id):
        try:
            data = Unique_identifier.objects.get(id=id)
            return data

        except Unique_identifier.DoesNotExist:
            return None

    def get(self,request,id):
        unique_identifier = self.get_object(id)
        if unique_identifier:
            serializer = UniqeIdentifierEditSerializer(unique_identifier)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        unique_identifier = self.get_object(id)
        if unique_identifier:
            serializer = UniqeIdentifierEditSerializer(unique_identifier,data=request.data) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        def delete(self,request,id):
            data = self.get_object(id)
            if data:
                data.delete()
                return Response(status=status.HTTP_202_ACCEPTED)

            return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

# Modify,Delete exisiting book
class BookEditView(APIView):
    permission_classes = [IsAdminUser | IsLibrarian]
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

# Book search by author
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

# Book search by genre
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

# Add Book request type(Issue,Return,Lost)
class BookRequestTypeView(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = BookRequestTypeSerializer

    def get(self,request):
        request_type = Book_request_type.objects.all()
        serializer = BookRequestTypeSerializer(request_type,many=True)
        return Response(serializer.data,status=status.HTTP_302_FOUND)

    def post(self,request):
        serializer = BookRequestTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

        return Response(serializer.error_messages,status=status.HTTP_406_NOT_ACCEPTABLE)

# Modify,Delete Book request type
class BookRequestTypeEditView(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = BookRequestTypeSerializer

    def get_object(self,id):
        try:
            book = Book_request_type.objects.get(id=id)
            return book

        except:
            return None

    def get(self,request,id):
        request_type = self.get_object(id)
        if request_type:
            serializer = BookRequestTypeSerializer(request_type)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        request_type = self.get_object(id)
        if request_type:
            serializer = BookRequestTypeSerializer(request_type,data=request.data) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        request_type = self.get_object(id)
        if request_type:
            request_type.delete()
            return Response(request.data,status=status.HTTP_202_ACCEPTED)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

# Display available books and search by author,genre
class AvailableBookView(APIView):
    permission_classes = [IsAdminUser|IsLibrarian|IsMember]
    serializer_class = GetBookSerializer

   
    def get(self,request):
        book_list = Unique_identifier.objects.filter(is_issue=False).values_list('book',flat=True).distinct()
        data_list = []
        if book_list:
            for info in book_list:
                data_list.append(info)

            books = Book.objects.filter(id__in=data_list)
            serializer = GetBookSerializer(books,many=True)

            return Response(serializer.data,status=status.HTTP_200_OK)
            
        return Response(request.data,status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
            
        user = request.user
        try:
            book = Book.objects.get(title=request.data['title'])
            book_get = Unique_identifier.objects.filter(book=book,is_issue=False)
            if user.issued_book < 2:
                # if book.no_copy > 0:
                if book_get:
                    
                    type = Book_request_type.objects.get(request_name="Issue")

                    request_check = Book_request.objects.filter(book=book,user=user,type=type)
                    issue_check = Book_request_log.objects.filter(book=book,user=user,type=type)

                    if request_check:
                        return Response({'details':'You alerady make the request for the book'},status=status.HTTP_208_ALREADY_REPORTED)
                        
                    if issue_check:
                        return Response({'details':'You alerady issued the book'},status=status.HTTP_208_ALREADY_REPORTED)

                    book_request= Book_request(book=book,date_issue=request.data['issue_date'],
                        date_return = request.data['return_date'],user=user, type=type
                    )
                    book_request.save()
                    return Response({'msg':'success'},status=status.HTTP_202_ACCEPTED)

                return Response({'error':'Book copy is not available try again'},status=status.HTTP_412_PRECONDITION_FAILED)

            return Response({'error':'Already reach maximum number of isseud book.Please return issued book and try again'},status=status.HTTP_412_PRECONDITION_FAILED)

        except Exception as e:
            print('Error',e.args)
            return Response({'error':'Book not available'},status=status.HTTP_400_BAD_REQUEST)
            
# Display all the request made by user           
class BookRequestView(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = BookRequestSerializer

    # Display all the request made by users
    def get(self,request):
        try:
            requests = Book_request.objects.all()
            serializer = BookRequestSerializer(requests,many=True)
            return Response(serializer.data,status=status.HTTP_302_FOUND)
        except:
            return Response({'error':'Please try again later'},status=status.HTTP_404_NOT_FOUND)

    # Search the request by book,type and user
    def post(self,request):
        pass_data ={}
        if "book" in request.data:
            pass_data['book'] = request.data['book']
        if "user" in request.data:
            pass_data['user'] = request.data['user']
        if "type" in request.data:
            pass_data['type'] = request.data['type']
            
        book_requests = Book_request.objects.filter(**pass_data)
        serializer = BookRequestSerializer(book_requests,many=True)
        return Response({'details':serializer.data},status=status.HTTP_302_FOUND)

        # serializer = BookRequestSerializer(data=request.data)
        # if serializer.is_valid():
        #     #serializer.save()
        #     return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

        # return Response(serializer.error_messages,status=status.HTTP_406_NOT_ACCEPTABLE)

# Modify, Delete the request
class BookRequestAddEditView(APIView):
    permission_classes = [IsLibrarian]
    serializer_class = BookRequestAddEditSerializer

    def get_object(self,id):
        try:
            request_info = Book_request.objects.get(id=id)
            return request_info
        except:
            return None

    def get(self,request,id):
        request_info = self.get_object(id)
        if request_info:
            serializer = BookRequestAddEditSerializer(request_info)
            return Response(serializer.data)

        return Response({'error':'No data Found'},status=status.HTTP_404_NOT_FOUND)

    def put(self,request,id):
        request_info = self.get_object(id)

        if request_info:

            if request.data['book'] == str(request_info.book.id) \
                and request.data['user'] == str(request_info.user.id) and request.data['type'] == str(request_info.type.id)\
                and request.data['date_issue'] != '' and request.data['date_return'] != '' :

                try:                
                    
                    msg =""
                    user = request_info.user
                    book = Book.objects.get(id=request_info.book.id)

                    if request_info.type.request_name == 'Issue':

                        try:
                            unique_identifier_data = Unique_identifier.objects.get(book=book,unique_no=request.data['unique_identifier'],is_issue=False,is_lost=False)
                        except Exception as e:
                            print('Error:',e)
                            return Response({'error':'Unique no of book is not match'},status=status.HTTP_400_BAD_REQUEST)

                        book_request = Book_request_log(
                            book=request_info.book,
                            unique_id = unique_identifier_data,
                            date_issue=request.data['date_issue'],
                            expected_date_return=request.data['date_return'],
                            user=request_info.user
                        )
                        # book.no_copy -=1
                        user.issued_book +=1 
                        book_request.type = request_info.type
                        book_request.save()
                        unique_identifier_data.is_issue = True
                        unique_identifier_data.save()
                        request_info.delete()
                        msg = "Book issued successfully."

                    if request_info.type.request_name == "Return":
                        book_request = Book_request_log.objects.get(book=book,user=user,type__request_name='Issue')
                        unique_identifier_data = Unique_identifier.objects.get(book=book,unique_no=request.data['unique_identifier'],is_issue=True)
                        # book.no_copy += 1
                        user.issued_book -= 1
                        today = date.today()
                        price = (today-book_request.expected_date_return)

                        if price.days > 0:
                            charge = 10 * price.days
                            # book_request.charge = charge
                        book_request.type = request_info.type
                        book_request.actual_date_return = request_info.return_lost_request_date
                        book_request.charge = request.data['charge']
                        book_request.save()
                        unique_identifier_data.is_issue = False
                        unique_identifier_data.save()
                        request_info.delete()
                        msg = "Book Return successfully."

                    if request_info.type.request_name == "Lost":
                        book_request = Book_request_log.objects.get(book=book,user=user,type__request_name='Issue')
                        unique_identifier_data = Unique_identifier.objects.get(book=book,unique_no=request.data['unique_identifier'],is_issue=True)
                        user.issued_book -= 1
                        today = date.today()
                        price = (today-book_request.expected_date_return)

                        if price.days > 0:
                            charge = 10 * price.days
                            # book_request.charge = charge
                        book_request.charge += book_request.book.price
                        book_request.type = request_info.type
                        book_request.actual_date_return = request_info.return_lost_request_date
                        book_request.charge = request.data['charge']
                        book_request.save()
                        unique_identifier_data.is_lost = True
                        unique_identifier_data.save()
                        request_info.delete()
                        msg = "Book is Lost and total amount paid."
                        

                    book.save()
                    user.save()
                    
                    return Response({'detail':msg},status=status.HTTP_202_ACCEPTED)

                except Exception as e:
                    print(e)
                    return Response({'error':'Request Type is wrong'},status=status.HTTP_400_BAD_REQUEST)       

            return Response({'error':'data is miss match'},status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':'No Request Found'},status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            request_info = self.get_object(id)
            request_info.delete()
            return Response(request_info,status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({'error':'Request Not Found'},status=status.HTTP_404_NOT_FOUND)

#  Get the csv of issued book
class IssuedBookView(APIView):
    permission_classes = [IsLibrarian]
    
    # def get(self,request):
    #     books = Book_issue.objects.all()
    #     serializer = BookIssueSerializer(books,many=True)
    #     return Response(serializer.data)

    def get(self, request):
        books =Book_request_log.objects.all()
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Book Title','Book Author','Book Unique Id','Member Name','Date Of Issue','Date of Return','Actual Date Return','Request Type','charge'])
        if books:
            for book in books.values_list('book__title','book__author__name','unique_id__unique_no','user__username','date_issue','expected_date_return','actual_date_return','type__request_name','charge'):
                writer.writerow(book)
            response['Content-Disposition'] = 'attachment; filename="book_issued.csv"'
            return response
        else:
            return Response({'details':'No Data Found'},status=status.HTTP_404_NOT_FOUND)

# Display issued book according to user login and make the return request
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
        books = Book_request_log.objects.filter(user=request.user,type__request_name='Issue')
        today = date.today()
        if books:
            data_list=[]
            for data in books:
                info = {}
                price = (today-data.expected_date_return)
                print(price.days)
                charge = 0
                if price.days > 0:
                    charge = 10 * price.days
                   
                info['book_name'] = data.book.title
                info['unique_id'] = data.unique_id.unique_no
                info['date_issue'] = data.date_issue
                info['date_return'] = data.expected_date_return
                info['user_name'] = data.user.username
                info['price'] = charge
                data_list.append(info)
            
            return Response(data_list,status=status.HTTP_302_FOUND)

        return Response({'detail':'There are no issue book.'},status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        
        try:
            user = CustomUser.objects.get(username=request.user.username)
            book = Book.objects.get(title=request.data['enter_book_name'])

            book_request_return_check = Book_request.objects.filter(book=book,user=request.user,type__request_name='Return')
            book_request_lost_check = Book_request.objects.filter(book=book,user=request.user,type__request_name='Lost')

            if book_request_return_check:
                return Response({'derails':'Book return request already present.'},status=status.HTTP_208_ALREADY_REPORTED)
            
            if book_request_lost_check:
                return Response({'derails':'Book lost request already present.'},status=status.HTTP_208_ALREADY_REPORTED)

            book_user_check = Book_request_log.objects.get(book=book,user=request.user,type__request_name='Issue')
            type = Book_request_type.objects.get(request_name="Return")

            today = date.today()
            price = (today-book_user_check.expected_date_return)
            charge = 0
            if price.days > 0:
                charge = 10 * price.days

            return_request = Book_request(book=book,date_issue=book_user_check.date_issue,\
                date_return=book_user_check.expected_date_return,return_lost_request_date=date.today(),\
                    user=user,type=type,charge=charge)
            return_request.save()
            return Response({'msg':'Book return request sent successfully.'},status=status.HTTP_202_ACCEPTED)

        except:
            return Response({'error':'Book not Found.'},status=status.HTTP_404_NOT_FOUND)
            
# Display issued book according to user login and make the lost request
class LostBookView(APIView):
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
        books = Book_request_log.objects.filter(user=request.user,type__request_name='Issue')
        today = date.today()
        if books:
            data_list=[]
            for data in books:
                info = {}
                price = (today-data.expected_date_return)
                print(price.days)
                charge = data.book.price
                if price.days > 0:
                    charge += 10 * price.days
                   
                info['book_name'] = data.book.title
                info['unique_id'] = data.unique_id.unique_no
                info['date_issue'] = data.date_issue
                info['date_return'] = data.expected_date_return
                info['user_name'] = data.user.username
                info['price'] = charge
                data_list.append(info)
            
            return Response(data_list,status=status.HTTP_302_FOUND)

        return Response({'detail':'There are no issue book.'},status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        
        try:
            user = CustomUser.objects.get(username=request.user.username)
            book = Book.objects.get(title=request.data['enter_book_name'])

            book_request_return_check = Book_request.objects.filter(book=book,user=request.user,type__request_name='Return')
            book_request_lost_check = Book_request.objects.filter(book=book,user=request.user,type__request_name='Lost')

            if book_request_return_check:
                return Response({'derails':'Book return request already present.'},status=status.HTTP_208_ALREADY_REPORTED)
            
            if book_request_lost_check:
                return Response({'derails':'Book lost request already present.'},status=status.HTTP_208_ALREADY_REPORTED)

            book_user_check = Book_request_log.objects.get(book=book,user=request.user,type__request_name='Issue')
            type = Book_request_type.objects.get(request_name="Lost")

            today = date.today()
            price = (today-book_user_check.expected_date_return)
            charge = book.price
            if price.days > 0:
                charge += 10 * price.days

            return_request = Book_request(book=book,date_issue=book_user_check.date_issue,\
                date_return=book_user_check.expected_date_return,return_lost_request_date=date.today(),\
                    user=user,type=type,charge=charge)
            return_request.save()
            return Response({'msg':'Book lost request sent successfully.'},status=status.HTTP_202_ACCEPTED)

        except:
            return Response({'error':'Book not Found.'},status=status.HTTP_404_NOT_FOUND)
            