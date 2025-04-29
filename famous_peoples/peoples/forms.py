from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import Category, Person, TagPost


class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Категория не выбрана', label='Категория')
    companion = forms.ModelChoiceField(queryset=Person.objects.filter(companion__isnull=True), empty_label='Нет партнера',
                                       required=False, label='Вторая половинка',
                                       help_text=mark_safe(
                                           '<span style="font-size: 16px; color: gray;">если партнера нет, значит он(а)'
                                           ' занят(а), либо его(её) нет на нашем сайте. Если его(её) нет на нашем сайте, Вы '
                                           'можете создать страницу с ним(ней), и потом уже указать партнера</span>'
                                       ))
    tag = forms.ModelMultipleChoiceField(queryset=TagPost.objects.all(), label='Теги',
                                         help_text='<span style="font-size: 16px; color: gray;">Для выбора нескольких '
                                                   'тегов удерживайте ctrl</span>',
                                         required=False)
    gender = forms.ChoiceField(choices=Person.Gender.choices, widget=forms.RadioSelect(), label='Пол')

    class Meta:
        model = Person
        fields = ('title', 'slug', 'gender', 'content', 'cat', 'companion', 'tag', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }
        labels = {
            'slug': 'URL',
            'gender': 'Пол'
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise ValidationError('Длина превышает 50 символов')
        return title


class UpdatePostForm(AddPostForm):
    class Meta(AddPostForm.Meta):
        exclude = ('slug', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'readonly': 'true'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['gender']


class ContactForm(forms.Form):
    fio = forms.CharField(max_length=200, label='ФИО', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Эл. Почта', widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=12, required=False, label='Номер телефона', widget=forms.TextInput(attrs={'class': 'form-input'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'cols': 30, 'rows': 7}), label='Сообщение')


