from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Course, Lesson, Video, Payment, UserCourse
from courses.forms import RegistrationForm
from courses.forms import LoginForm
from django.views import View
from django.contrib.auth import logout,authenticate,login
import paypalrestsdk
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import uuid
# Create your views here.
def home(request):      
    courses = Course.objects.all()
    print(courses)
    return render(request,template_name='courses/home.html',context={"courses":courses})

def coursePage(request,slug):
    course = Course.objects.get(slug = slug) 
    serial_number = request.GET.get('lecture')

    if serial_number is None:
        serial_number = 1
    video = Video.objects.get(serial_number = serial_number , course =course)

    if((request.user.is_authenticated is False) and (video.is_preview is False)):
        return redirect("login")

    context = {
        "course" : course,
        "video" : video
    }
    return render(request,template_name="courses/course_page.html",context=context)

class SignupView(View):
    def get(self,request):
        form = RegistrationForm()
        return render(request,template_name="courses/signup.html",context={"form":form})
    
    def post(self,request):
        form = RegistrationForm(request.POST)
        if(form.is_valid()):
            user = form.save()
            if(user is not None):
                return redirect("login")
        return render(request,template_name="courses/signup.html",context={"form":form})

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, template_name="courses/login.html", context={"form": form})

    def post(self, request):
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

        return render(request, template_name="courses/login.html", context={"form": form})
    

def signout(request):
    logout(request)
    return redirect("home")

    


@login_required(login_url='/login')
def checkout(request, slug):
    course = Course.objects.get(slug=slug)

    action = request.GET.get("action")

    order = None
    if action == 'create_payment':
        print("Creating Order Object")
        order = "Order Created"

    context = {
        "course" : course,
        "order" : order
    }
    return render(request, template_name="courses/check_out.html", context=context)