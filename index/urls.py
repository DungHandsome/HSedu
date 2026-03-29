from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_dispatch, name='dashboard_dispatch'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/<str:id>/', views.teacher_student_profile, name='teacher_student_profile'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('chats/', views.chat_room_list, name='chat_room_list'),
    path('chats/<uuid:thread_id>/', views.chat_room, name='chat_room'),
    path('class/<int:id>/manage/', views.main_class_manage, name='main_class_manage'),
    path('eclass/<int:eclass_id>/create-announcement/', views.create_announcement, name='create_announcement'),


    # 1. Submit email form
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='auth/password-reset.html'), 
         name='password_reset'),
    
    # 2. Success message after email sent
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password-reset-haveemailed.html'), 
         name='password_reset_done'),
    
    # 3. The link clicked in the email (token verification)
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password-reset-confirm.html'), 
         name='password_reset_confirm'),
    
    # 4. Success message after password change
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password-reset-success.html'), 
         name='password_reset_complete'),
]

