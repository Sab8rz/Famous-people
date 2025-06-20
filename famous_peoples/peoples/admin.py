from dal import autocomplete
from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Category, Person, TagPost

class CompanionFilter(admin.SimpleListFilter):
    title = 'Статус'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('have_companion', 'Есть вторая половинка'),
            ('single', 'Нет второй половинки'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'have_companion':
            return queryset.filter(companion__isnull=False)
        elif self.value() == 'single':
            return queryset.filter(companion__isnull=True)


@admin.register(Person)
class BasePersonAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_create', 'is_published', 'cat', 'gender', 'companion')
    list_display_links = ('title', )
    ordering = ['-time_create', 'title']
    list_editable = ('is_published', )
    actions = ('set_published', 'set_draft')
    search_fields = ('title__startswith', 'cat__name')
    list_filter = (CompanionFilter, 'cat__name', 'is_published')
    fields = ('title', 'slug', 'gender', 'content', 'photo', 'post_photo', 'cat', 'companion', 'tag')
    prepopulated_fields = {'slug': ('title', )}
    filter_horizontal = ('tag', )
    readonly_fields = ('post_photo', )
    autocomplete_fields = ('companion', )

    class Media:
        js = [
            'admin/js/jquery.init.js',
            'autocomplete_light/jquery.init.js',
            'autocomplete_light/autocomplete.init.js',
            'autocomplete_light/vendor/select2/dist/js/select2.full.js',
        ]
        css = {
            'screen': [
                'autocomplete_light/vendor/select2/dist/css/select2.css',
                'autocomplete_light/autocomplete.css',
            ],
        }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'companion':
            kwargs['widget'] = autocomplete.Select2(url='person-autocomplete',
                                                    attrs={
                                                        'data-placeholder': 'Введите имя...',
                                                        'data-minimum-input-length': 0,
                                                    }
                                                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Изображение')
    def post_photo(self, obj):
        if obj.photo:
            return mark_safe(f"<img src='{obj.photo.url}' width=50>")
        return 'Без фото'

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        model = self.model
        count = queryset.update(is_published=model.Status.PUBLISHED)
        self.message_user(request, f"{count} записей были опубликованы", messages.WARNING)

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        model = self.model
        count = queryset.update(is_published=model.Status.DRAFT)
        self.message_user(request, f"{count} записи были сняты с публикации", messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name', )
    prepopulated_fields = {'slug': ('name', )}


@admin.register(TagPost)
class TagPostAdmin(admin.ModelAdmin):
    list_display = ('tag', )
    list_display_links = ('tag', )
    prepopulated_fields = {'slug': ('tag', )}