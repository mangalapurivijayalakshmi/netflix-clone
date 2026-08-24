from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Movie


@receiver(post_save, sender=Movie)
def notify_users_new_movie(sender, instance, created, **kwargs):
    

    if created:
        users = User.objects.filter(is_active=True).exclude(email='')
        recipient_list = [user.email for user in users]
        

        if recipient_list:
            send_mail(
                subject=f"🎬 New Movie Added: {instance.title}",
                message=f"Hi! A new movie '{instance.title}' has just been added to Netflix Clone. Check it out now!",
                from_email=None,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            