from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
from .models import Course, Lesson, Video, Payment, UserCourse, Quizzy, Question, Answer
from courses.forms import RegistrationForm
from courses.forms import LoginForm
from django.views import View
from django.contrib.auth import logout,login
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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
    courses = Course.objects.all() 
    print(courses)
    return render(request,template_name='courses/home.html',context={"courses":courses})


    

def coursePage(request,slug):
    course = Course.objects.get(slug = slug) 
    serial_number = request.GET.get('lecture')

    if serial_number is None:
        serial_number = 1
    video = Video.objects.get(serial_number = serial_number , course =course)

    if (video.is_preview is False):

        if request.user.is_authenticated is False:
            return redirect("login")
        else:
            user = request.user
            try:
                user_course = UserCourse.objects.get(user = user  , course = course)
            except:
                return redirect("check-out" , slug=course.slug)

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
    error = None

    try:
        user_course = UserCourse.objects.get(user=user, course=course)
        error = "You are already enrolled in this course."
    except UserCourse.DoesNotExist:
        pass

    amount = course.price - (course.price * course.discount * 0.01)

    if amount <= 0:
        user_course = UserCourse(user=user, course=course)
        user_course.save()
        return redirect('my-courses')

    payment = Payment(user=user, course=course, price=amount, order_id=str(uuid.uuid4()))
    if error is None:
        payment.save()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(amount),
        'item_name': course.title,
        'invoice': payment.order_id,
        'currency_code': 'USD',
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('payment_success', kwargs={'slug': course.slug})),
        'cancel_return': request.build_absolute_uri(reverse('payment_cancel', kwargs={'slug': course.slug})),
    }
    paypal_payment = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "course" : course,
        'paypal': paypal_payment,
        "error": error
    }

    return render(request, template_name="courses/check_out.html", context=context)


@login_required(login_url='/login')
def payment_success(request, slug):
    course = Course.objects.get(slug=slug)
    user = request.user

    payment = Payment.objects.filter(user=user, course=course, status=False).first()
    if payment:
        payment.status = True  
        payment.save()

        user_course = UserCourse(user=user, course=course)
        user_course.save()
        payment.user_course = user_course
        payment.save()

    return render(request, 'courses/payment_success.html', {'course': course})



@login_required(login_url='/login')
def payment_cancel(request, slug):
    course = Course.objects.get(slug=slug)
    return render(request, 'courses/payment_cancel.html', {'course': course})





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

