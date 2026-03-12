import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
# Create your models here.

class EClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    school_year = models.CharField(max_length=9) # e.g., "2023-2024"
    main_teacher = models.OneToOneField('Teacher', on_delete=models.SET_NULL, null=True, related_name='main_teacher')
    subjects = models.ManyToManyField('Subject', related_name='classes', blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Core fields
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #Detailed fields
    full_name = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_teacher = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.username

class Announcement(models.Model):
    eclass = models.ForeignKey(EClass, on_delete=models.CASCADE, related_name='announcements')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.eclass.name}"

class AnnouncementFile(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='announcements/files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.announcement.title}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    classes = models.ForeignKey(EClass, on_delete=models.CASCADE, related_name='students', blank=True, null=True)
    attendance = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    #MAJOR_SUBJECT = [
    #    (1, 'Toán Học'),
    #    (2, 'Văn Học'),
    #    (3, 'Tiếng Anh'),
    #    (4, 'Vật Lý'),
    #    (5, 'Hóa Học'),
    #    (6, 'Sinh Học'),
    #    (7, 'Lịch Sử'),
    #    (8, 'Địa Lý'),
    #    (9, 'Giáo Dục Thể Chất'),
    #    (10, 'Giáo Dục Quốc Phòng và An Ninh'),
    #    (11, 'Tin Học'),
    #    (12, 'Âm Nhạc'),
    #]


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    classes = models.ManyToManyField(EClass, related_name='teachers', blank=True)
    major_subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Exercise(models.Model):
    eclass = models.ManyToManyField(EClass, related_name='exercises', blank=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    time_limit = models.IntegerField(help_text="Time limit in minutes", blank=True, null=True, validators=[MinValueValidator(1)])
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.title
    
class Question(models.Model):
    type = models.BooleanField(default=False, help_text="True = Multiple Choice, False = Short Answer")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='questions')
    questions = models.TextField()
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Question for {self.exercise.title}"
    
class ExerciseResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exercise_results')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='exercise_results')
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.exercise.title} - {self.score}"
    
class Thread(models.Model):
    # UUIDs are better for chat room URLs than simple IDs (security by obscurity)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # If this is a Class Group Chat, link it here. 
    # If it's a Private DM, this stays null.
    eclass = models.OneToOneField(
        'EClass', 
        on_delete=models.CASCADE, 
        related_name='chat_thread', 
        null=True, 
        blank=True
    )
    
    # For private DMs, we track the two participants.
    # For Class Chats, participants are managed via the EClass.students relationship.
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='threads', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def is_group_chat(self):
        return self.eclass is not None

    def __str__(self):
        if self.eclass:
            return f"Group: {self.eclass.name}"
        return f"Private Thread: {self.id}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # Great for "Unread" notifications

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"
    
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



# Storing score and grades and subjects of students
class GradeRecord(models.Model):
    # Defining the Choices
    GRADE_LEVEL_CHOICES = [
        (10, '10th Grade'),
        (11, '11th Grade'),
        (12, '12th Grade'),
    ]
    TERM_CHOICES = [
        (1, 'Term 1'),
        (2, 'Term 2'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Year/Grade context
    grade_level = models.IntegerField(choices=GRADE_LEVEL_CHOICES)
    term = models.IntegerField(choices=TERM_CHOICES)

    # The actual score
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )

    class Meta:
        # Prevents duplicate scores for the same student in the same subject/term
        unique_together = ('student', 'subject', 'grade_level', 'term')

    def __str__(self):
        return f"{self.student.user.full_name} - {self.subject.name} (G{self.grade_level} T{self.term})"
    
