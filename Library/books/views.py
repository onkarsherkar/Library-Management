from django.http.response import JsonResponse
from django.shortcuts import render
from django.http.response import JsonResponse,HttpResponse
from rest_framework import permissions
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework import generics
from .models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def test(request):
    return JsonResponse({'test':'OK'})

class RegisterView(APIView):
    
    #queryset = CustomUser.objects.all()
    #serializer_class = RegisterSerializer
    #authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAdminUser]
    def get(self,request):
        #if request.user.is_anonymous:
        return Response({'data':'You can register'},status=status.HTTP_200_OK)
        #else:
            #return Response({'data':'Logout then register'},status=status.HTTP_400_BAD_REQUEST)


    def post(self,request):
        #if request.user.is_anonymous:
        serializer= RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        #return Response({'error':'please log out and then register'},status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def get(self,request):
        if request.user.is_anonymous:
            return Response({'data':'You can register'},status=status.HTTP_200_OK)
        else:
            return Response({'data':'Logout then register'},status=status.HTTP_400_BAD_REQUEST)

    
    def post(self,request):
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
    def get(self,request):
        #if request.user.is_authenticated:
        logout(request)
        return Response({'data':'logout Successfully..'},status=status.HTTP_200_OK)
        
        #return Response({'error':'User Not Found..'},status=status.HTTP_400_BAD_REQUEST)