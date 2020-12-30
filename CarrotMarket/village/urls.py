from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from village.views import ArticleViewSet, CommentViewSet

app_name = 'village'

router = SimpleRouter()
router.register('feed', ArticleViewSet, basename='feed')
# router.register('comment', CommentViewSet, basename='comment')

urlpatterns = router.urls