menu = [
    {'title': "Все", 'url_name': 'peoples'},
    {'title': "Мужчины", 'url_name': 'men'},
    {'title': "Женщины", 'url_name': 'women'},
    {'title': "Обратная связь", 'url_name': 'contact'},
    {'title': "О сайте", 'url_name': 'about'},
]


class DataMixin:
    title_page = None
    paginate_by = 3

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context['title'] = self.title_page
        context['menu'] = menu
        context.update(kwargs)
        return context

