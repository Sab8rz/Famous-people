from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from . import forms
from .tasks import send_registration_email


class LoginUser(LoginView):
    form_class = forms.LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class RegisterUser(CreateView):
    form_class = forms.RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        send_registration_email.delay(user.email, user.username)
        return super().form_valid(form)


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = forms.ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользователя'}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = forms.UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'
    extra_context = {'title': 'Изменение пароля'}


class UserPasswordReset(PasswordResetView):
    form_class = forms.UserPasswordResetForm
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    extra_context = {'title': 'Сброс пароля'}
    success_url = reverse_lazy('users:password_reset_done')