from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import peoples.models as m
from peoples.custom_permissions import IsAdminOrReadOnly
from peoples.serializers import CategorySerializer, PersonSerializer
from django.core.cache import cache


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


    def list(self, request, *args, **kwargs):
        cache_key = 'api_person_list'
        if data := cache.get(cache_key) is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 15)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'api_person_{instance.pk}'
        if data := cache.get(cache_key) is None:
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, 60 * 30)
        return Response(data)