from rest_framework import serializers
from .models import Category, Person


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class PersonSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Person
        fields = ['title', 'slug', 'content', 'gender', 'cat', 'author']