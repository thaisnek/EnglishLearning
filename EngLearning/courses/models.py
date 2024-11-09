from django.db import models
from django.utils.text import slugify
import uuid
from django.contrib.auth.models import User
# Create your models here.



class Course(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, null=False,default='default-slug')
    description = models.CharField(max_length=500, null=True, blank=True)
    discount = models.IntegerField(null=False,default=0)
    price = models.IntegerField(null=False)
    active = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="files/thumbnail")
    date = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField(null=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())
        super().save(*args, **kwargs)




class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def getCourseName(self):
        return self.course.name

    def __str__(self):
        return f'{self.title} - {self.course.name}'
    



class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=500, default="")
    video_id = models.CharField(max_length=100,null=False)
    serial_number = models.IntegerField(null=True, blank=True)
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title




class CourseProperty(models.Model):
    description = models.CharField(max_length=500, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    on_delete = models.CASCADE

    class Meta:
        abstract = True




class Tag(CourseProperty):
    pass



class Prerequisite(CourseProperty):
    pass



class Learnings(CourseProperty):
    pass



class UserCourse(models.Model):
    user = models.ForeignKey(User , null = False , on_delete=models.CASCADE)
    course = models.ForeignKey(Course , null = False , on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.course.name}'
    



class Payment(models.Model):
    order_id = models.CharField(max_length = 50 , null = False)
    price = models.IntegerField(null=False,default=0)
    user_course = models.ForeignKey(UserCourse , null = True , blank = True ,  on_delete=models.CASCADE)
    user = models.ForeignKey(User ,  on_delete=models.CASCADE)
    course = models.ForeignKey(Course , on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.course.name}'





class Quizzy(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,unique=True)
    score = models.IntegerField(default=0)
    
    def getCourseName(self):
        return self.lesson.getCourseName()
    
    def getLessonName(self):
        return self.lesson.title

    def __str__(self):
        return f'{self.id}-{self.lesson.title}-{self.lesson.getCourseName()}'


class Question(models.Model):
    quizzy = models.ForeignKey(Quizzy, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f'{self.quizzy.title}-{self.quizzy.getLessonName()}-{self.quizzy.getCourseName()}'

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tof = models.BooleanField()
    text = models.TextField()

    def __str__(self):
        return f'{self.question.text}'


class CouponCode(models.Model):
    code = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='coupons')
    discount = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.course.name}'