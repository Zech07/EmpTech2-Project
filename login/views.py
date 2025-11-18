from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from pos.models import Customer, Driver, Staff, Admin
from django.db.models.signals import post_save
from django.dispatch import receiver


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')  # 'customer', 'staff', 'admin', 'driver'

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists. Please choose another.")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        group = Group.objects.get(name=role)
        user.groups.add(group)  
        user.save()  # signal will now run correctly
        return redirect('login:login')

    
    return render(request, 'register.html')

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on group
            if user.groups.filter(name='admin').exists():
                return redirect('pos:reports')
            elif user.groups.filter(name='staff').exists():
                return redirect('pos:cashier')
            elif user.groups.filter(name='driver').exists():
                return redirect('deliveries:delivery_list')
            else:
                return redirect('customer:profile')
        else:
            return HttpResponse("Invalid credentials. Please try again.")

    return render(request, 'login.html')





@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Define the roles and their corresponding models
    role_model_map = {
        "customer": Customer,
        "driver": Driver,
        "staff": Staff,
        "admin": Admin,
    }

    # Get the first group of the user, if any
    group = instance.groups.first()
    
    if group is None:
        # If no group assigned, create default groups if they don't exist
        for role_name in role_model_map.keys():
            Group.objects.get_or_create(name=role_name)
        return  # You may want to skip profile creation until a group is assigned

    role = group.name.lower()

    # Create the corresponding profile model
    model_class = role_model_map.get(role)
    if model_class:
        if role == "customer":
            model_class.objects.get_or_create(user=instance, defaults={"name": instance.username})
        else:  # driver, staff, admin
            model_class.objects.get_or_create(user=instance, defaults={"full_name": instance.username})