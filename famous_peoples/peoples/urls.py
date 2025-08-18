from django.urls import path, include
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'person', PersonViewSet, basename='person')

urlpatterns = [
    path('', home, name='home'),
    path('persons/', Peoples.as_view(), name='peoples'),
    path('men/', Men.as_view(), name='men'),
    path('women/', Women.as_view(), name='women'),
    path('about/', about, name='about'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('add-page/', AddPage.as_view(), name='add_page'),
    path('contact/', contact, name='contact'),
    path('category/<slug:cat_slug>/', Category.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', TagPostList.as_view(), name='tag'),
    path('edit/<slug:slug>/', UpdatePage.as_view(), name='edit_page'),
    path('person-autocomplete/', PersonAutocomplete.as_view(), name='person-autocomplete'),
    path('api/', include(router.urls), name='persons-api')
]