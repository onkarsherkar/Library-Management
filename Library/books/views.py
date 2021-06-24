from django.http.response import JsonResponse
from django.shortcuts import render
from django.http.response import JsonResponse
# Create your views here.

def test(request):
    return JsonResponse({'test':'OK'})