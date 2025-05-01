from django.shortcuts import render
from django.http import HttpResponse

def user_home(request):
    return HttpResponse("Welcome to the user section.")
