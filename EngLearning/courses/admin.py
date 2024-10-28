from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.
class TagAdmin(admin.TabularInline):
    model = Tag

class PrerequisiteAdmin(admin.TabularInline):
    model = Prerequisite

class LearningsAdmin(admin.TabularInline):
    model = Learnings 

class VideoAdmin(admin.TabularInline):
    model = Video

class CourseAdmin(admin.ModelAdmin):
    inlines = [TagAdmin, LearningsAdmin, PrerequisiteAdmin, VideoAdmin]
    list_display = ["name" , 'get_price' , 'get_discount' , 'active']
    list_filter = ("discount" , 'active')

    def get_discount(self , course):
        return f'{course.discount} %'
    
    def get_price(self , course):
        return f'$ {course.price}'
    
    get_discount.short_description= "Discount"
    get_price.short_description = "Price"


class PaymentAdmin(admin.ModelAdmin):
    model = Payment   
    list_display = [ "order_id" , 'get_user' , 'get_course' , 'status'] 
    list_filter = ["status" , 'course']

    def get_user(self , payment):
        return format_html(f"<a target='_blank' href='/admin/auth/user/{payment.user.id}'>{payment.user}</a>")
    

    def get_course(self , payment):
        return format_html(f"<a target='_blank' href='/admin/courses/course/{payment.course.id}'>{payment.course}</a>")

    get_course.short_description = "Course"
    get_user.short_description = "User"



class UserCourseAdminModel(admin.ModelAdmin):
    model = UserCourse   
    list_display = ['user_course' , 'get_user' , 'get_course'] 
    list_filter = ['course']

    def get_user(self , usercourse):
        return format_html(f"<a target='_blank' href='/admin/auth/user/{usercourse.user.id}'>{usercourse.user}</a>")
    
    def user_course(self , usercourse):
        return "Open"
    

    def get_course(self , usercourse):
        return format_html(f"<a target='_blank' href='/admin/courses/course/{usercourse.course.id}'>{usercourse.course}</a>")

    get_course.short_description = "Course"
    get_user.short_description = "User"

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Payment , PaymentAdmin)
admin.site.register(UserCourse , UserCourseAdminModel)
admin.site.register(Quizzy)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(CouponCode)
