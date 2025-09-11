import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from peoples.models import Person, Category, TagPost


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(username='TestUser', email='test@test.com', password='Test_Password')


@pytest.fixture
def category():
    return Category.objects.create(name='Наука', slug='science')


@pytest.fixture
def tag1():
    return TagPost.objects.create(tag='Физик', slug='physic')


@pytest.fixture
def tag2():
    return TagPost.objects.create(tag='Математик', slug='math')


@pytest.mark.django_db
def test_person_create(user, category):
    """Создание объекта Person"""
    person = Person.objects.create(
            title='Никола Тесла',
            slug='nikola-tesla',
            content='прославился своими работами в области электротехники и радио',
            gender=Person.Gender.MALE,
            cat=category,
            author=user
    )

    assert person.title == 'Никола Тесла'
    assert person.slug == 'nikola-tesla'
    assert person.content == 'прославился своими работами в области электротехники и радио'
    assert person.gender == Person.Gender.MALE
    assert person.cat == category
    assert person.author == user
    assert str(person) == 'Никола Тесла'
    assert person.get_absolute_url() == reverse('post', kwargs={'post_slug': 'nikola-tesla'})
    assert person.is_published == Person.Status.PUBLISHED


@pytest.mark.django_db
def test_clean_companion_own(category):
    """Нельзя выбрать себя в партнеры"""
    person = Person(title='title', slug='slug', gender=Person.Gender.FEMALE, cat=category)
    person.companion = person

    with pytest.raises(ValidationError):
        person.full_clean()


@pytest.mark.django_db
def test_clean_companion_gender(category):
    """Партнеры должны быть разного пола"""
    male = Person.objects.create(title='Male', slug='male', gender=Person.Gender.MALE, cat=category)
    female = Person.objects.create(title='Female', slug='female', gender=Person.Gender.FEMALE, cat=category)

    # Правильно
    male.companion = female
    male.full_clean()

    # Неправильно
    male2 = Person.objects.create(title='Male2', slug='male2', gender=Person.Gender.MALE, cat=category)
    male.companion = male2

    with pytest.raises(ValidationError):
        male.full_clean()


@pytest.mark.django_db
def test_save_companions(category):
    """При установке партнера автоматически устанавливается companion у партнера"""
    m = Person.objects.create(title='Mal', slug='mal', gender=Person.Gender.MALE, cat=category)
    f = Person.objects.create(title='Fem', slug='fem', gender=Person.Gender.FEMALE, cat=category)

    m.companion = f
    m.save()

    f.refresh_from_db()
    assert f.companion == m
    assert m.companion == f


@pytest.mark.django_db
def test_save_companions_clear(category):
    """При удалении партнера, у партнера тоже обнуляется companion"""
    m = Person.objects.create(title='Mal', slug='mal', gender=Person.Gender.MALE, cat=category)
    f = Person.objects.create(title='Fem', slug='fem', gender=Person.Gender.FEMALE, cat=category)

    m.companion = f
    m.save()

    m.companion = None
    m.save()

    f.refresh_from_db()
    assert f.companion is None
    assert m.companion is None


@pytest.mark.django_db
def test_person_tags(category, tag1, tag2):
    person = Person.objects.create(title='Альберт Эйнштейн', slug='albert-einstein', gender=Person.Gender.MALE, cat=category)
    person.tag.add(tag1, tag2)

    assert tag1, tag2 in person.tag.all()