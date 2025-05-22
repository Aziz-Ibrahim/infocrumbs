from django.shortcuts import render, redirect
from django.contrib.auth import logout


# home
def home(request):
    return render(request, 'core/home.html')
