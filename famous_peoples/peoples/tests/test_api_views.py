import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED
from rest_framework.test import APIClient
from peoples.models import Person, Category
from django.core.cache import cache
from .test_models import user
from .test_views import category, published_person


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return get_user_model().objects.create_superuser(username='TestAdmin', password='Admin_Password')


@pytest.fixture
def api_client_as_user(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_as_admin(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
def test_category_delete_read(api_client, category):
    """GET /category-delete/{id}/"""
    url = reverse('category-delete', kwargs={'pk': category.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_category_delete_destroy_only_admin(api_client_as_admin, category):
    """Удалить категорию может только админ"""
    url = reverse('category-delete', kwargs={'pk': category.pk})
    response = api_client_as_admin.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_category_delete_destroy_unauth(api_client, category):
    """Неавторизованный пользователь не может удалить категорию"""
    url = reverse('category-delete', kwargs={'pk': category.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_category_delete_auth_not_admin(api_client_as_user, category):
    """Авторизованный пользователь (не админ) не может удалить категорию"""
    url = reverse('category-delete', kwargs={'pk': category.pk})
    response = api_client_as_user.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_person_list(api_client, published_person):
    """GET список личностей"""
    cache.clear()
    response = api_client.get(reverse('person-list'))
    assert Person.objects.count() == 1
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert any(p['title'] == 'Уильям Мортон' for p in response.data)


@pytest.mark.django_db
def test_person_create_unauth(api_client, category, published_person):
    """Неавторизованный пользователь не может создать личность"""
    url = reverse('person-list')
    data = {
        'title': 'New',
        'slug': 'slug',
        'is_published': published_person.is_published,
        'gender': published_person.gender,
        'cat': category.id
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_person_create_auth(api_client_as_user, category, published_person):
    """Авторизованный пользователь может создать личность"""
    url = reverse('person-list')
    data = {
        'title': 'New',
        'slug': 'slug',
        'is_published': published_person.is_published,
        'gender': published_person.gender,
        'cat': category.id
    }
    response = api_client_as_user.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'New'


@pytest.mark.django_db
def test_person_categories_read(api_client, category):
    """Список всех категорий"""
    response = api_client.get(reverse('person-categories'))
    assert response.status_code == status.HTTP_200_OK
    assert 'Категории' in response.data
    assert category.name in response.data['Категории']


@pytest.mark.django_db
def test_person_categories_create_unauth(api_client, category):
    """Неавторизованный пользователь не может создавать категории"""
    url = reverse('person-categories')
    data = {
        'name': 'New',
        'slug': 'new'
    }
    response = api_client.post(url, data)
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_person_categories_create_unauth(api_client_as_user, category):
    """Авторизованный пользователь не может создавать категории"""
    url = reverse('person-categories')
    data = {
        'name': 'New',
        'slug': 'new'
    }
    response = api_client_as_user.post(url, data)
    assert response.status_code == HTTP_201_CREATED
    assert response.data['name'] == 'New'


@pytest.mark.django_db
def test_person_read(api_client, published_person):
    """GET личности"""
    url = reverse('person-detail', kwargs={'pk': published_person.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == published_person.title


@pytest.mark.django_db
def test_person_update_unauth(api_client, published_person):
    """PUT неавторизованный пользователь не может полностью обновить личность"""
    url = reverse('person-detail', kwargs={'pk': published_person.pk})
    response = api_client.put(url, {'title': 'New title'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_person_update_auth(api_client_as_user, published_person):
    """PUT авторизованный пользователь может полностью обновить личность"""
    url = reverse('person-detail', kwargs={'pk': published_person.pk})
    data = {
        'title': 'New',
        'slug': 'slug',
        'is_published': published_person.is_published,
        'gender': published_person.gender,
        'cat': published_person.cat.id
    }
    response = api_client_as_user.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'New'


@pytest.mark.django_db
def test_person_partial_update_unauth(api_client, published_person):
    """PATCH неавторизованный пользователь не может частично обновить личность"""
    url = reverse('person-detail', kwargs={'pk': published_person.pk})
    response = api_client.patch(url, {'title': 'New title'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_person_partial_update_auth(api_client_as_user, published_person):
    """PATCH авторизованный пользователь может частично обновить личность"""
    url = reverse('person-detail', kwargs={'pk': published_person.pk})
    response = api_client_as_user.patch(url, {'title': 'New title'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'New title'


@pytest.mark.django_db
def test_person_category_read(api_client, published_person):
    """Получить категорию личности"""
    url = reverse('person-category', kwargs={'pk': published_person.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'Категория' in response.data
    assert response.data['Категория'] == published_person.cat.name


@pytest.mark.django_db
def test_person_category_update_unath(api_client, published_person, category):
    """Неавторизованный не может обновить категорию у личности"""
    url = reverse('person-category', kwargs={'pk': published_person.pk})
    data = {
        'name': 'Наука',
        'slug': 'nauka'
    }
    response = api_client.put(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_person_category_update_auth(api_client_as_user, published_person, category):
    """Авторизованный пользователь может обновить категорию у личности"""
    url = reverse('person-category', kwargs={'pk': published_person.pk})
    data = {
        'name': 'Комики',
        'slug': 'komiki'
    }
    response = api_client_as_user.put(url, data)
    published_person.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Комики'
    assert response.data['slug'] == 'komiki'