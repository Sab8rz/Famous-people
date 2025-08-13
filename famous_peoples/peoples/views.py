from dal_select2.views import Select2QuerySetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from rest_framework import generics, viewsets, routers, mixins, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from peoples import forms
import peoples.models as m
from peoples.custom_permissions import IsAdminOrReadOnly
from peoples.utils import DataMixin
from peoples.serializers import CategorySerializer, PersonSerializer


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def home(request):
    return render(request, "peoples/home.html")


class Peoples(DataMixin, ListView):
    template_name = 'peoples/index.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs),
                                      title='Все личности',
                                      cat_selected=0
                                      )

    def get_queryset(self):
        return m.Person.published.all().select_related('cat')


class Men(DataMixin, ListView):
    template_name = 'peoples/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs),
                                      title='Мужчины',
                                      cat_selected=0
                                      )

    def get_queryset(self):
        return m.Person.published.filter(gender='M').select_related('cat')


class Women(DataMixin, ListView):
    template_name = 'peoples/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs),
                                      title='Женщины',
                                      cat_selected=0
                                      )

    def get_queryset(self):
        return m.Person.published.filter(gender='F').select_related('cat')


class Category(DataMixin, ListView):
    template_name = 'peoples/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория - ' + cat.name,
                                      cat_selected=cat.pk
                                      )

    def get_queryset(self):
        return m.Person.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')


class ShowPost(DataMixin, DetailView):
    template_name = 'peoples/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'])

    def get_object(self):
        return get_object_or_404(m.Person.published, slug=self.kwargs[self.slug_url_kwarg])


def about(request):
    return render(request, "peoples/about.html", {'title': 'О нас'})


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = forms.AddPostForm
    template_name = 'peoples/addpage.html'
    title_page = 'Добавление статьи'

    def get_context_data(self, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs))

    def form_valid(self, form):
        person = form.save(commit=False)
        person.author = self.request.user
        person.save()

        if person.is_published == m.Person.Status.PUBLISHED:
            return redirect(person.get_absolute_url())
        else:
            return redirect('peoples')


class UpdatePage(LoginRequiredMixin, DataMixin, UpdateView):
    model = m.Person
    form_class = forms.UpdatePostForm
    template_name = 'peoples/addpage.html'
    title_page = 'Редактирование статьи'

    def get_context_data(self, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs))

    def form_valid(self, form):
        person = form.save(commit=False)
        person.author = self.request.user
        person.save()

        return redirect(person.get_absolute_url())


def contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = forms.ContactForm()
    return render(request, 'peoples/contact.html', {'form': form, 'title': 'Обратная связь'})


class TagPostList(DataMixin, ListView):
    template_name = 'peoples/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = m.TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        return m.Person.published.filter(tag__slug=self.kwargs['tag_slug']).select_related('cat')

class PersonAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = m.Person.objects.all()
        if self.q:
            qs = qs.filter(title__icontains=self.q)
        return qs

    def get_result_label(self, item):
        return f"{item.title} ({item.get_gender_display()})"


# API
class CategoryAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = m.Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )


class PersonViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    queryset = m.Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @action(methods=['get', 'put'], detail=True, serializer_class=CategorySerializer)
    def category(self, request, pk=None):
        person = self.get_object()
        cat = person.cat

        if request.method == 'GET':
            return Response({'Категория': cat.name})

        elif request.method == 'PUT':
            serializer = CategorySerializer(cat, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

    @action(methods=['get', 'post'], detail=False, serializer_class=CategorySerializer)
    def categories(self, request):
        if request.method == 'GET':
            cats = m.Category.objects.all()
            return Response({'Категории': [c.name for c in cats]})

        elif request.method == 'POST':
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)


router = routers.SimpleRouter()
router.register(r'person', PersonViewSet, basename='person')


