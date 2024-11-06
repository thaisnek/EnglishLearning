from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
from .models import Course, Lesson, Video, Payment, UserCourse, Quizzy, Question, Answer, CouponCode
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



# Create your views here.


from django.core.paginator import Paginator

def home(request):
    course_list = Course.objects.filter(active=True)
    paginator = Paginator(course_list,8)  # Hiển thị n khóa học mỗi trang

    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    return render(request, 'courses/home.html', {'courses': courses})



@login_required(login_url='/login')
def my_courses(request):
    user = request.user
    user_courses = UserCourse.objects.filter(user=user)
    context = {
        'user_courses' : user_courses
    }
    return render(request,template_name='courses/my_course.html',context=context)  



def coursePage(request,slug):
    course = Course.objects.get(slug = slug) 
    serial_number = request.GET.get('lecture')
    videos = course.video_set.all().order_by("serial_number")
    next_lecture = 2
    previous_lecture = None
    if serial_number is None:
        serial_number = 1
    else:
        next_lecture = int(serial_number)+1
        if len(videos) < next_lecture:
            next_lecture = None
        previous_lecture = int(serial_number)-1


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
        "video" : video,
        "next_lecture" : next_lecture,
        "previous_lecture" : previous_lecture
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
    couponcode = request.GET.get('couponcode')
    coupon_code_message = None
    coupon = None
    try:
        user_course = UserCourse.objects.get(user=user, course=course)
        error = "You are already enrolled in this course."
    except UserCourse.DoesNotExist:
        pass

    amount = course.price - (course.price * course.discount * 0.01)

    if couponcode:
        try:
            coupon = CouponCode.objects.get(course=course, code=couponcode)
            amount = course.price - (course.price * coupon.discount * 0.01)
        except:
            coupon_code_message = "Invalid Coupon Code"
            print("Coupon Code Invalid")

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
        'item_name': course.name,
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
        "error": error,
        "coupon" : coupon,
        "coupon_code_message" : coupon_code_message
    }

    return render(request, template_name="courses/check_out.html", context=context)



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




def payment_cancel(request, slug):
    course = Course.objects.get(slug=slug)
    return render(request, 'courses/payment_cancel.html', {'course': course})





#quizzy
#quizzy
def QuizzyListView(request):
    quizzes = Quizzy.objects.all()
    return render(request, 'courses/quizzy_list.html', {'quizzes': quizzes})

def QuestionListView(request, quizzy_id):
    quizzy = get_object_or_404(Quizzy, id=quizzy_id)
    questions = Question.objects.filter(quizzy=quizzy)
    question_count = questions.count()  # Đếm số lượng câu hỏi
    course_slug = quizzy.lesson.course.slug

    # Reset điểm số về 0 khi bắt đầu quiz
    quizzy.score = 0
    quizzy.save()

    context = {
        'questions': questions,
        'quizzy': quizzy,
        'course_slug': course_slug,
        'question_count': question_count,  # Thêm số lượng câu hỏi vào context
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

        quizzy = question.quizzy
        if correct:
            quizzy.score += 1
            quizzy.save()

        next_question = Question.objects.filter(quizzy=question.quizzy, id__gt=question_id).first()
        
        response_data = {
            'correct': correct,
            'next_question_id': next_question.id if next_question else None,
            'current_score': quizzy.score  # Trả về điểm số hiện tại
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)
