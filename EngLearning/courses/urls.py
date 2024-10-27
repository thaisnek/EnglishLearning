from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',home,name='home'),
    path('logout/',signout,name='logout'),
    path('signup/',SignupView.as_view(),name='signup'),
    path('login/',LoginView.as_view(),name='login'),
    path('course/<str:slug>/',coursePage,name='coursepage'),
    path('check-out/<str:slug>/',checkout,name='check-out'),
    path('payment-success/<str:slug>/', payment_success, name='payment_success'),
    path('payment-failed/<str:slug>/', payment_cancel, name='payment_cancel'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('quizzes/', QuizzyListView, name='quizzy-list'),
    path('quizzes/<int:quizzy_id>/questions/', QuestionListView, name='question-list'),
    path('questions/<int:question_id>/', question_detail, name='question-detail'),
    path('questions/<int:question_id>/answers/', AnswerListView, name='answer-list'),
    path('check-answer/', check_answer, name='check-answer'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
