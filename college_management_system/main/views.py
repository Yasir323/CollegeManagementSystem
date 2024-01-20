from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login


from college_management_system.main.models import CustomUser, AdminHOD
from college_management_system.staff.models import Staff
from college_management_system.student.models import Student


def home(request):
    return render(request, "home.html")


def contact(request):
    return render(request, "contact.html")


def login_user(request):
    return render(request, "login_page.html")


def do_login(request):
    email_id = request.POST.get("email")
    password = request.POST.get("password")
    if not (email_id and password):
        messages.error(request, "Please provide all the details!")
        return render(request, "login_page.html")

    user = CustomUser.objects.filter(email=email_id, password=password).last()
    if not user:
        messages.error(request, "Invalid Login Credentials!")
        return render(request, "login_page.html")

    login(request, user)

    if user.user_type == CustomUser.STUDENT:
        return redirect("student_home/")
    elif user.user_type == CustomUser.STAFF:
        return redirect("staff_home/")
    elif user.user_type == CustomUser.HOD:
        return redirect("admin_home/")
    return render(request, "home.html")


def registration(request):
    return render(request, "registration.html")


def get_user_type_from_email(email):
    try:
        user_type = email.split("@")[0].split(".")[1]
        return CustomUser.EMAIL_TO_USER_TYPE_MAP[user_type]
    except:
        return None


def do_registration(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")

    if not (first_name and last_name and email and password):
        messages.error(request, "Please provide all the details!")
        return render(request, "registration.html")

    is_user_exists = CustomUser.objects.filter(email=email).exists()
    if is_user_exists:
        messages.error(request, "The email is already in use.")
        return render(request, "registration.html")

    if password != confirm_password:
        messages.error(request, "Both passwords should match!")
        return render(request, "registration.html")

    user_type = get_user_type_from_email(email)
    # TODO: Prevent student from registering as a staff
    if user_type is None:
        messages.error(request, "Please use valid format for the email")
        return render(request, "registration.html")

    username = email.split('@')[0].split('.')[0]

    if CustomUser.objects.filter(username=username).exists():
        messages.error(request, 'User with this username already exists. Please use different username')
        return render(request, 'registration.html')

    user = CustomUser()
    user.username = username
    user.email = email
    user.password = password
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    if user_type == CustomUser.STAFF:
        Staff.objects.create(admin=user)
    elif user_type == CustomUser.STUDENT:
        Student.objects.create(admin=user)
    elif user_type == CustomUser.HOD:
        AdminHOD.objects.create(admin=user)
    return render(request, 'login_page.html')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
