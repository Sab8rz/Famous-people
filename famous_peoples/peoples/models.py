from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=self.model.Status.PUBLISHED)


class Person(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    class Gender(models.TextChoices):
        MALE = 'M', 'Мужчина'
        FEMALE = 'F', 'Женщина'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    content = models.TextField(blank=True, verbose_name='Описание')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.IntegerField(choices=Status.choices, default=Status.PUBLISHED, verbose_name='Статус')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None, blank=True, null=True, verbose_name='Фото')
    gender = models.CharField(choices=Gender.choices, verbose_name='Пол')
    companion = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='partner',
                                     verbose_name='Партнер')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Категория')
    tag = models.ManyToManyField('TagPost', blank=True, related_name='tags')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True,
                               default=None)
    objects = models.Manager()
    published = PublishedModel()


    class Meta:
        verbose_name = "Известная личность"
        verbose_name_plural = "Известные личности"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.companion == self:
            raise ValidationError('Нельзя выбрать себя в партнеры')

        if self.companion and self.gender == self.companion.gender:
            raise ValidationError('Партнер должен быть противоположного пола')

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.companion:
            partner = self.companion
            if partner.companion != self:
                partner.companion = self
                partner.save()
        else:
            try:
                old_partner = Person.objects.get(companion=self)
                old_partner.companion = None
                old_partner.save()
            except Person.DoesNotExist:
                pass


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


