import pytest
from django.urls import reverse

from peoples.models import Person
from peoples.tests.test_views import client, category
from peoples.tests.test_models import user


@pytest.fixture
def person(category, user):
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
def test_login_post(client):
    pass