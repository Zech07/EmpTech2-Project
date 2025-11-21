from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib import messages
from pos.models import Customer, Staff
from django.db.models.signals import post_save
from django.dispatch import receiver


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'customer')  # 'customer', 'staff', 'admin', 'driver'

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, 'register.html')

        # Create user with additional fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Assign to appropriate group
        try:
            group = Group.objects.get(name=role)
            user.groups.add(group)
            user.save()
            
            messages.success(request, f"Account created successfully! You can now login as {role}.")
            return redirect('login:login')
            
        except Group.DoesNotExist:
            messages.error(request, "Invalid role selected.")
            user.delete()
            return render(request, 'register.html')

    return render(request, 'register.html')

def login_user(request):    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Check if there's a next parameter
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Use direct URL paths instead of reverse()
            if user.groups.filter(name='admin').exists() or (hasattr(user, 'staff') and user.staff.is_admin()):
                return redirect('/pos/dashboard/sales/')  # Direct path
            elif user.groups.filter(name='staff').exists() or hasattr(user, 'staff'):
                return redirect('/pos/orders/')  # Direct path
            elif user.groups.filter(name='driver').exists() or (hasattr(user, 'staff') and user.staff.is_driver()):
                return redirect('/pos/orders/')  # Direct path
            else:  # customer
                return redirect('/pos/orders/')  # Direct path
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Check if user has any groups
    if not instance.groups.exists():
        # Default to customer if no group assigned
        Customer.objects.get_or_create(
            user=instance,
            defaults={
                "phone": "",
                "address": ""
            }
        )
        return

    # Get the first group (primary role)
    group = instance.groups.first()
    role = group.name.lower()

    if role == "customer":
        Customer.objects.get_or_create(
            user=instance,
            defaults={
                "phone": "",
                "address": ""
            }
        )

    elif role in ["driver", "staff", "admin"]:
        # Map group names to position values
        position_map = {
            "driver": "driver",
            "staff": "staff", 
            "admin": "admin"
        }
        
        position = position_map.get(role, "staff")
        
        Staff.objects.get_or_create(
            user=instance,
            defaults={
                "phone": "",
                "position": position
            }
        )