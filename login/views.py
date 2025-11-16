from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from pos.models import Customer

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password') 

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists. Please choose another.")
        
        Customer.objects.create(name=username, phone='', address='')

        user = User(username=username, email=email)
        user.set_password(password)  
        user.save()
        return redirect('login')

    
    return render(request, 'register.html')

def login_user(request):    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  
            return redirect('pos:customers')
        else:
            return redirect('login')
    return render(request, 'login.html')
