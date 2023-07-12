"""URL-роутинг приложения API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import FollowUserView, SubscriptionsView
from users.views import CustomUserViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/', SubscriptionsView.as_view()),
    path('users/<int:id>/subscribe/', FollowUserView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
