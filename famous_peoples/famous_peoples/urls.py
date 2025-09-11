from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from famous_peoples import settings
from peoples.views import page_not_found
from peoples.api_views import CategoryAPIDestroy
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='Известные личности API',
        default_version='v1',
        description='API для работы с информацией об известных личностях'
    )
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('peoples.urls'), name='people-app'),
    path('api/category-delete/<int:pk>/', CategoryAPIDestroy.as_view()),
    path('users/', include('users.urls', namespace='users')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('__debug__/', include('debug_toolbar.urls')),
]

handler404 = page_not_found

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)