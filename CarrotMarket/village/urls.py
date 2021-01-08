from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import SimpleRouter, Route
from village.views import ArticleViewSet

app_name = 'village'

router = SimpleRouter()
router.register('feed', ArticleViewSet, basename='feed')

urlpatterns = [
    path('', include(router.urls)),
]
