# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import EClass, Thread, Student, Teacher, AnnouncementFile

@receiver(post_save, sender=EClass)
def create_class_chat_thread(sender, instance, created, **kwargs):
    """
    Automatically create a Chat Thread when a new Class is created.
    """
    if created:
        # Create the thread and link it to the new class
        new_thread = Thread.objects.create(eclass=instance)
        
        # Add all teachers of the class to the thread participants
        for teacher in instance.teachers.all():
            new_thread.participants.add(teacher.user)
            
        # Note: Students are added to participants dynamically 
        # in the view based on EClass membership, not here.

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a Student or Teacher profile based on the is_teacher flag.
    """
    if created:
        if instance.is_teacher:
            Teacher.objects.get_or_create(user=instance)
        else:
            # If not a teacher, assume they are a student
            Student.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the profile whenever the User is saved.
    """
    # Use hasattr to prevent errors if the profile hasn't been created yet
    if instance.is_teacher and hasattr(instance, 'teacher'):
        instance.teacher.save()
    elif hasattr(instance, 'student'):
        instance.student.save()


@receiver(post_delete, sender=AnnouncementFile)
def delete_file_on_model_delete(sender, instance, **kwargs):
    """
    Deletes the physical file from the MEDIA_ROOT when the 
    AnnouncementFile record is deleted from the database.
    """
    if instance.file:
        # This deletes the file from storage
        instance.file.delete(save=False)