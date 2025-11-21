from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib import messages
from pos.models import Customer, Staff
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


def register_user(request):
    # Ensure default groups exist
    default_groups = ['customer', 'staff', 'admin', 'driver']
    for group_name in default_groups:
        Group.objects.get_or_create(name=group_name)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'customer')

        # Validation
        if not all([username, email, password, role]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use another email.")
            return render(request, 'register.html')

        # Initialize user variable
        user = None

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Assign to selected group
            group = Group.objects.get(name=role)
            user.groups.add(group)
            user.save()

            # Create appropriate profile based on role
            if role == 'customer':
                Customer.objects.create(user=user, phone="", address="")
                messages.success(request, "Customer account created successfully! You can now login.")
            elif role in ['staff', 'admin', 'driver']:
                position_map = {
                    'staff': 'staff',
                    'admin': 'admin', 
                    'driver': 'driver'
                }
                Staff.objects.create(
                    user=user, 
                    phone="", 
                    position=position_map.get(role, 'staff')
                )
                messages.success(request, f"{role.capitalize()} account created successfully! You can now login.")
            
            return redirect('login:login')

        except Group.DoesNotExist:
            messages.error(request, "Invalid role selected.")
            if user:
                user.delete()
            return render(request, 'register.html', {'roles': default_groups})
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            if user:
                user.delete()
            return render(request, 'register.html', {'roles': default_groups})

    # For GET request, show available roles
    available_roles = ['customer', 'staff', 'admin', 'driver']
    return render(request, 'register.html', {'roles': available_roles})


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
                return redirect('/pos/dashboard/sales/')
            elif user.groups.filter(name='staff').exists() or hasattr(user, 'staff'):
                return redirect('/pos/orders/')
            elif user.groups.filter(name='driver').exists() or (hasattr(user, 'staff') and user.staff.is_driver()):
                return redirect('/pos/orders/')
            else:  # customer
                return redirect('/pos/orders/')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login:login')


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    """
    Backup signal to create profiles for users created outside registration form
    """
    if created:
        # Only create customer profile by default
        # Other profiles will be created in register view or admin
        if not instance.groups.exists():
            Customer.objects.get_or_create(user=instance, defaults={"phone": "", "address": ""})