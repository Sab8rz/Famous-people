from django import template
from django.db.models import Count
from peoples.models import Category, TagPost


register = template.Library()


@register.inclusion_tag('peoples/list_categories.html')
def show_categories(cat_selected_id=0):
    cats = Category.objects.annotate(total=Count('posts')).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected_id}


@register.inclusion_tag('peoples/list_tags.html')
def show_all_tags():
    return {'tags': TagPost.objects.annotate(total=Count('tags')).filter(total__gt=0)}


