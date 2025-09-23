import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from pytest_django.asserts import assertRedirects
from peoples.models import Person, Category, TagPost
from django.core.cache import cache


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(username='TestUser', email='test@test.com', password='Test_Password')


@pytest.fixture
def category():
    return Category.objects.create(name='История', slug='istoriya')

@pytest.fixture
def tag():
    return TagPost.objects.create(tag='Революция', slug='revolyutsiya')


@pytest.fixture
def published_person(category, user):
    return Person.objects.create(
        title='Лев Троцкий',
        slug='lev-trotskiy',
        is_published=Person.Status.PUBLISHED,
        gender=Person.Gender.MALE,
        cat=category,
        author=user
    )


@pytest.fixture
def draft_person(category, user):
    return Person.objects.create(
        title='Черновик',
        slug='chernovik',
        is_published=Person.Status.DRAFT,
        gender=Person.Gender.FEMALE,
        cat=category,
        author=user
    )


@pytest.mark.django_db
def test_home_view(client):
    """Загрузка главной страницы"""
    response = client.get(reverse('home'))

    assert 'peoples/home.html' in [t.name for t in response.templates]
    assert response.status_code == 200


@pytest.mark.django_db
def test_peoples_list_view(client, published_person):
    """Загрузка страницы всех опубликованных личностей"""
    cache.clear()

    response = client.get(reverse('peoples'))

    assert 'peoples/index.html' in [t.name for t in response.templates]
    assert 'posts' in response.context
    assert published_person in response.context['posts']
    assert response.context['title'] == 'Все личности'
    assert response.status_code == 200


@pytest.mark.django_db
def test_men_list_view(client, published_person):
    """Загрузка страницы только с мужчинами"""
    cache.clear()

    response = client.get(reverse('men'))

    assert 'peoples/index.html' in [t.name for t in response.templates]
    assert 'posts' in response.context
    assert published_person in response.context['posts']
    assert response.context['title'] == 'Мужчины'
    assert all(p.gender == Person.Gender.MALE for p in response.context['posts'])
    assert response.status_code == 200


@pytest.mark.django_db
def test_women_list_view(client, published_person):
    """Загрузка страницы только с женщинами"""
    cache.clear()

    woman = Person.objects.create(
        title='Анна Ахматова',
        slug='anna-ahmatova',
        is_published=Person.Status.PUBLISHED,
        gender=Person.Gender.FEMALE,
        cat=published_person.cat,
        author=published_person.author
    )
    response = client.get(reverse('women'))

    assert 'peoples/index.html' in [t.name for t in response.templates]
    assert 'posts' in response.context
    assert woman in response.context['posts']
    assert response.context['title'] == 'Женщины'
    assert all(p.gender == Person.Gender.FEMALE for p in response.context['posts'])
    assert response.status_code == 200


@pytest.mark.django_db
def test_category_list_view(client, published_person):
    """Загрузка страницы определенной категории"""
    cache.clear()

    category = published_person.cat
    url = reverse('category', kwargs={'cat_slug': category.slug})
    response = client.get(url)

    assert 'peoples/index.html' in [t.name for t in response.templates]
    assert 'posts' in response.context
    assert response.context['title'] == 'Категория - ' + category.name
    assert all(p.cat == category for p in response.context['posts'])
    assert response.status_code == 200


@pytest.mark.django_db
def test_show_post_view(client, published_person):
    """Страница конкретной личности"""
    cache.clear()

    url = reverse('post', kwargs={'post_slug': published_person.slug})
    response = client.get(url)

    assert 'peoples/post.html' in [t.name for t in response.templates]
    assert 'post' in response.context
    assert response.context['title'] == published_person
    assert response.context['post'] == published_person
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_view(client):
    """Страница 'О нас'"""
    response = client.get(reverse('about'))

    assert 'peoples/about.html' in [t.name for t in response.templates]
    assert 'title' in response.context
    assert response.context['title'] == 'О нас'
    assert response.status_code == 200


@pytest.mark.django_db
def test_show_post_draft(client, draft_person):
    """Страница с черновиком недоступна"""
    url = reverse('post', kwargs={'post_slug': draft_person.slug})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_add_page_redirect_unauthorized(client):
    """Перенаправление неавторизованного пользователя при попытке создать пост"""
    url = reverse('add_page')
    response = client.get(url)

    assertRedirects(response, f'/users/login/?next={url}')


@pytest.mark.django_db
def test_add_page_open_authorized(client, user):
    """Доступ к странице создания поста для авторизованного пользователя"""
    client.login(username=user.username, password='Test_Password')
    response = client.get(reverse('add_page'))

    assert 'peoples/addpage.html' in [t.name for t in response.templates]
    assert response.context['title'] == 'Добавление статьи'
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_page_create_authorized(client, category, user):
    """Создание поста для авторизованного пользователя"""
    client.login(username=user.username, password='Test_Password')
    data = {
        'title': 'New person',
        'slug': 'new-person',
        'gender': Person.Gender.MALE,
        'content': 'descr',
        'cat': category.id,
        'tag': [],
    }
    response = client.post(reverse('add_page'), data)
    person = Person.objects.get(slug='new-person')

    assertRedirects(response, person.get_absolute_url())


@pytest.mark.django_db
def test_update_page_open_unauthorized(client, published_person):
    """Перенаправление неавторизованного пользователя при попытке редактировать пост"""
    url = reverse('edit_page', kwargs={'slug': published_person.slug})
    response = client.get(url)

    assertRedirects(response, f'/users/login/?next={url}')


@pytest.mark.django_db
def test_update_page_open_authorized(client, published_person, user):
    """Доступ к странице редактирования поста для авторизованного пользователя"""
    client.login(username=user.username, password='Test_Password')
    response = client.get(reverse('edit_page', kwargs={'slug': published_person.slug}))

    assert 'peoples/addpage.html' in [t.name for t in response.templates]
    assert response.context['title'] == 'Редактирование статьи'
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_page_edit_authorized(client, published_person, category, user):
    """Редактирование поста для авторизованного пользователя"""
    client.login(username=user.username, password='Test_Password')
    url = reverse('edit_page', kwargs={'slug': published_person.slug})
    data = {
        'title': published_person.title,
        'slug': published_person.slug,
        'content': 'new content',
        'gender': published_person.gender,
        'cat': category.pk
    }
    response = client.post(url, data)
    published_person.refresh_from_db()

    assertRedirects(response, published_person.get_absolute_url())


@pytest.mark.django_db
def test_contact_get(client):
    """GET-запрос страницы обратной связи"""
    response = client.get(reverse('contact'))

    assert 'peoples/contact.html' in [t.name for t in response.templates]
    assert 'form' in response.context
    assert response.context['title'] == 'Обратная связь'
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_post(client):
    """POST-запрос страницы обратной связи"""
    url = reverse('contact')
    data = {
        'fio': 'Фамилия Имя Отчество',
        'email': 'email@email.com',
        'phone': '+79995553241',
        'content': 'текст'
    }
    response = client.post(url, data)

    assert 'peoples/contact.html' in [t.name for t in response.templates]
    assert 'form' in response.context
    assert response.context['title'] == 'Обратная связь'
    assert response.status_code == 200


@pytest.mark.django_db
def test_tag_post_list_view(client, published_person, tag):
    """Загрузка страницы по определенному тегу"""
    cache.clear()

    published_person.tag.add(tag)
    url = reverse('tag', kwargs={'tag_slug': tag.slug})
    response = client.get(url)

    assert 'peoples/index.html' in [t.name for t in response.templates]
    assert 'posts' in response.context
    assert response.context['title'] == 'Тег: ' + tag.tag
    assert all(tag in p.tag.all() for p in response.context['posts'])
    assert response.status_code == 200


