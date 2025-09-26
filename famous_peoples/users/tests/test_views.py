import pytest
from django.urls import reverse

from peoples.models import Person
from peoples.tests.test_views import client, category
from peoples.tests.test_models import user


@pytest.fixture
def person(category):
    return Person.objects.create(
        title='Уильям Мортон',
        slug='uilyam-morton',
        is_published=Person.Status.PUBLISHED,
        gender=Person.Gender.MALE,
        cat=category
    )


@pytest.mark.django_db
def test_login_get(client):
    """GET: загрузка страница входа"""
    response = client.get(reverse('users:login'))
    assert response.status_code == 200
    assert 'users/login.html' in [t.name for t in response.templates]
    assert response.context['title'] == 'Авторизация'


@pytest.mark.django_db
def test_login_post_valid(client, user):
    """Успешный вход"""
    response = client.post(reverse('users:login'), {'username': 'TestUser', 'password': 'Test_Password'})
    assert response.url == reverse('home')


@pytest.mark.django_db
def test_login_post_invalid(client):
    """Неверный пароль"""
    response = client.post(reverse('users:login'), {'username': 'TestUser', 'password': 'WrongPassword'})
    assert response.status_code == 200
    assert 'Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.' in response.content.decode()