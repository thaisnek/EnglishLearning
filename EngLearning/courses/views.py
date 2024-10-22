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
    user = request.user
    action = request.GET.get('action')
    error = None

    # Kiểm tra nếu người dùng đã đăng ký khóa học
    try:
        user_course = UserCourse.objects.get(user=user, course=course)
        error = "You are already enrolled in this course."
    except UserCourse.DoesNotExist:
        pass

    amount = course.price - (course.price * course.discount * 0.01)

    # Nếu giá trị thanh toán bằng 0, tự động đăng ký khóa học
    if amount <= 0:
        userCourse = UserCourse(user=user, course=course)
        userCourse.save()
        return redirect('my-courses')

    if action == 'create_payment':
        # Thông tin thanh toán cho PayPal
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': amount,
            'item_name': course.title,
            'invoice': f"{user.id}-{course.id}-{timezone.now().timestamp()}",
            'currency_code': 'USD',
            'return': request.build_absolute_uri(reverse('payment_success')),  # URL để chuyển hướng khi thanh toán thành công
            'cancel_return': request.build_absolute_uri(reverse('payment_cancel')),  # URL để chuyển hướng khi thanh toán bị hủy
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'paypal/checkout.html', {'form': form})

    context = {
        "course": course,
        "error": error,
    }
    return render(request, template_name="courses/check_out.html", context=context)

# Thêm các hàm xử lý thành công và hủy thanh toán
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('txn_id')
        invoice = request.POST.get('invoice')

        user_id, course_id, _ = invoice.split('-')
        user = UserCourse.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)

        user_course = UserCourse.objects.get(user=user, course=course)

        payment = Payment(
            payment_id=payment_id,
            user_course=user_course,
            user=user,
            course=course,
            status=True,
        )
        payment.save()

        return render(request, 'paypal/success.html', {'course': course})
    return HttpResponse("Payment was not successful")

def payment_cancel(request):
    return render(request, 'paypal/cancel.html', context={})