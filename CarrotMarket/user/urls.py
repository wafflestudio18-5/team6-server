from rest_framework.routers import SimpleRouter
from django.urls import include, path
from user.views import UserViewSet


app_name = 'user'

router = SimpleRouter()
router.register('user', UserViewSet, basename='user')

urlpatterns = router.urls
