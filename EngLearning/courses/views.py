from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from .models import Course, Lesson, Video, Payment, UserCourse, Quizzy, Question, Answer
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



from django.shortcuts import get_object_or_404

def check_answer(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        question_id = request.POST.get('question_id')
        answer = get_object_or_404(Answer, id=answer_id)
        question = get_object_or_404(Question, id=question_id)
        correct = answer.tof

        next_question = Question.objects.filter(quizzy=question.quizzy, id__gt=question_id).first()
        
        response_data = {
            'correct': correct,
            'next_question_id': next_question.id if next_question else None,
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Create your views here.


def home(request):      
    courses = Course.objects.all() # lấy toàn bộ khóa học
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
    
    def post(self,request): # tạo nếu hợp lệ
        form = RegistrationForm(request.POST)
        if(form.is_valid()):
            user = form.save()
            if(user is not None):
                return redirect("login")
        return render(request,template_name="courses/signup.html",context={"form":form})

class LoginView(View):
    def get(self, request): # hiển thị biểu mẫu 
        form = LoginForm()
        return render(request, template_name="courses/login.html", context={"form": form})

    def post(self, request): # xử lý biểu mẫu và đăng nhập nếu hợp lệ
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

def checkout(request, slug): 
    course = Course.objects.get(slug=slug) # lấy thông tin chi tiết dựa vào slug
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


    order = None
    if action == 'create_payment':
        print("Creating Order Object")
        order = "Order Created"

    context = {
        "course" : course,
        "order" : order
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



#quizzy
def QuizzyListView(request):
    quizzes = Quizzy.objects.all()
    return render(request, 'courses/quizzy_list.html', {'quizzes': quizzes})

def QuestionListView(request, quizzy_id):
    questions = Question.objects.filter(quizzy_id=quizzy_id)
    quizzy = Quizzy.objects.get(id=quizzy_id)
    course_slug = quizzy.lesson.course.slug
    context = {
        'questions': questions,
        'course_slug': course_slug,
    }
    return render(request, 'courses/question_list.html', context)


#ans
def AnswerListView(resquest):
    ans = Answer.objects.all()
    data = [{"id" : answer.id, "text" : answer.text, "tof" : answer.text, "quesstion" : answer.question.id} for answer in ans]
    return JsonResponse(data,safe = False)

# hiển thị câu hỏi và câu trả lời
def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question)
    context = {
        'question': question,
        'answers': answers,
    }
    return render(request, 'courses/question_detail.html', context)
