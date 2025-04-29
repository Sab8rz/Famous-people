menu = [
    {'title': "Все", 'url_name': 'peoples'},
    {'title': "Мужчины", 'url_name': 'men'},
    {'title': "Женщины", 'url_name': 'women'},
    {'title': "Обратная связь", 'url_name': 'contact'},
    {'title': "О сайте", 'url_name': 'about'},
]


class DataMixin:
    title_page = None
    extra_content = {}
    paginate_by = 3

    def __init__(self):
        if self.title_page:
            self.extra_content['title'] = self.title_page

        if 'menu' not in self.extra_content:
            self.extra_content['menu'] = menu

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context['title'] = self.title_page

        context['menu'] = menu
        context['cat_selected'] = None
        context.update(kwargs)
        return context

