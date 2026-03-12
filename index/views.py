from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Q
from .forms import SignUpForm, AnnouncementForm
from .models import Student, Teacher, Thread, EClass, AnnouncementFile, Announcement

# Authentication Views
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 1. Save the User
                user = form.save(commit=False)
                user.full_name = form.cleaned_data.get('full_name')
                user.is_teacher = form.cleaned_data.get('is_teacher')
                user.save()

                # 2. Create the linked Profile
                with transaction.atomic():
                    user = form.save()

                    if user.is_teacher:
                        Teacher.objects.get_or_create(user=user, defaults={'major': form.cleaned_data.get('major')})
                    else:
                        Student.objects.get_or_create(user=user)

                # 3. Log the user in
                login(request, user, backend='index.login_check_both.EmailOrUsernameBackend')
                return redirect('dashboard_dispatch') # Redirect to dashboard dispatch page
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    # login_check_both.py will handle authentication, so no need to override form_valid here


# Dashboard Views
@login_required
def dashboard_dispatch(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')

@login_required
def student_dashboard(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    # 1. Get the current user
    student_obj = get_object_or_404(Student, user=request.user)
    # 2. Get all classes the student is in
    enrolled_classes = EClass.objects.filter(students=student_obj)
    
    # 3. Get recent announcements from these classes
    recent_announcements = Announcement.objects.filter(
        eclass__in=enrolled_classes
    ).order_by('-created_at')[:5] # Limit to top 5
    
    context = {
        'enrolled_classes': enrolled_classes,
        'recent_announcements': recent_announcements,
    }
    
    return render(request, 'student/student_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    # 1. Get Teacher Profile
    teacher_profile = get_object_or_404(Teacher, user=request.user)

    # 2. Find the class where they are the "Main Teacher" (Homeroom)
    # Using the related_name='main_teacher' from EClass model
    main_class = EClass.objects.filter(main_teacher=teacher_profile).first()

    # 3. Get all classes they teach (Subject Classes)
    # Using the related_name='teachers' from Teacher.classes field
    all_taught_classes = teacher_profile.classes.all()

    # 4. Get recent announcements they've posted
    my_announcements = Announcement.objects.filter(teacher=request.user)[:5]

    context = {
        'teacher_profile': teacher_profile,
        'main_class': main_class,
        'all_taught_classes': all_taught_classes,
        'my_announcements': my_announcements,
    }

    return render(request, 'teacher/teacher_dashboard.html', context)


# Announcement Upload View (for teachers)
@login_required
def create_announcement(request, eclass_id):
    eclass = get_object_or_404(EClass, id=eclass_id)
    
    if request.method == 'POST':
        # Form only validates title and content
        form = AnnouncementForm(request.POST) 
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.eclass = eclass
            announcement.teacher = request.user
            announcement.save()

            # Manually process the files
            # 'files' must match the 'name' attribute in HTML
            files = request.FILES.getlist('files') 
            for f in files:
                AnnouncementFile.objects.create(
                    announcement=announcement,
                    file=f
                )
            
            return redirect('eclass_detail', pk=eclass_id)
    else:
        form = AnnouncementForm()
    
    return render(request, 'teacher/create_announcement.html', {'form': form, 'eclass': eclass})

# Chat Views
@login_required
def chat_room_list(request):
    # Shows all group chats for classes the user is in, and their private chats
    
    # This filter line only filter threads that the user is a participant of, so it only includes private threads that the user is in, and group threads for classes the user is in (since those threads also include the user as a participant)
    #threads = Thread.objects.filter(participants=request.user)
    user = request.user
    threads = Thread.objects.filter(
        Q(participants=user) | 
        Q(eclass__students__user=user) |
        Q(eclass__teachers__user=user)
    ).distinct() # Distinct to avoid duplicates
    return render(request, 'chat/room_list.html', {'threads': threads})

@login_required
def chat_room(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    user = request.user

    # --- FIX STARTS HERE ---
    
    # Check if user is a participant (for private chats)
    is_participant = user in thread.participants.all()
    
    # Check if user is a student or teacher of the class (for class chats)
    is_class_member = False
    if thread.eclass:
        is_student = thread.eclass.students.filter(user=user).exists()
        is_teacher = thread.eclass.teachers.filter(user=user).exists()
        is_class_member = is_student or is_teacher

    # Deny access if not a participant AND not a class member
    if not (is_participant or is_class_member):
        return render(request, '403.html', status=403)
        
    messages = thread.messages.all().order_by('timestamp')
    return render(request, 'chat/room.html', {'thread': thread, 'messages': messages})