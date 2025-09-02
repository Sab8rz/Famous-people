from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from peoples.models import Person
from random import choice


@shared_task
def send_registration_email(email, username):
    send_mail(
        subject='Добро пожаловать',
        message=f'Спасибо за регистрацию {username}.\nДобро пожаловать на наш сайт посвященный известным личностям',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_password_reset_email(email, subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_daily_greeting():
    person = choice(list(Person.published.all()))
    mail_users = get_user_model().objects.filter(is_active=True, email__isnull=False, email__contains='@mail.ru')
    for user in mail_users:
        send_mail(
            subject=f'Приветствие от {person.title}',
            message=f'{user.username}, {person.title} передает тебе привет!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )