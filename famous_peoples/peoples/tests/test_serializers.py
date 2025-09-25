import pytest
from unittest.mock import Mock

from peoples.serializers import *
from peoples.models import Person
from .test_models import user
from .test_views import category


@pytest.fixture
def person(category, user):
    return Person.objects.create(
        title='Уильям Мортон',
        slug='uilyam-morton',
        gender=Person.Gender.MALE,
        cat=category,
        author=user
    )


@pytest.mark.django_db
def test_category_serializer_valid(category):
    """Category: валидность сериализатора"""
    serializer = CategorySerializer(category)
    data = serializer.data
    assert data['name'] == 'История'
    assert data['slug'] == 'istoriya'


@pytest.mark.django_db
def test_category_serializer_create():
    """Category: создание категории"""
    data = {
        'name': 'Медицина',
        'slug': 'medicina'
    }
    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()

    serializer.save()
    assert serializer.data['name'] == 'Медицина'
    assert serializer.data['slug'] == 'medicina'


@pytest.mark.django_db
def test_category_serializer_update(category):
    """Category: обновление категории"""
    data = {
        'name': 'Update',
        'slug': 'update'
    }
    serializer = CategorySerializer(category, data=data)
    assert serializer.is_valid()

    serializer.save()
    assert serializer.data['name'] == 'Update'
    assert serializer.data['slug'] == 'update'


@pytest.mark.django_db
def test_person_serializer_valid(person, category, user):
    """Person: валидность сериализатора"""
    serializer = PersonSerializer(person)
    data = serializer.data
    assert data['title'] == 'Уильям Мортон'
    assert data['slug'] == 'uilyam-morton'
    assert data['cat'] == category.id


@pytest.mark.django_db
def test_person_serializer_author_read_only(category, user):
    """Person: нельзя сменить автора"""
    data = {
        'title': 'Title',
        'slug': 'title',
        'content': 'content',
        'gender': 'M',
        'cat': category.id,
        'author': 423
    }
    serializer = PersonSerializer(data=data, context={'request': Mock(user=user)})
    assert serializer.is_valid()

    person = serializer.save()
    assert person.author == user