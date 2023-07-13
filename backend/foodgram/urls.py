"""Конфигурация роутингов основного приложения foodgram."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

app_name = 'foodgram'

urlpatterns = [
    path('api/', include('users.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
