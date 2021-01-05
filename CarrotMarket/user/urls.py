from allauth.account.views import confirm_email
from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from user.views import *

app_name = 'user'

router = SimpleRouter()
router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include((router.urls))),
    # 어드민 페이지
#    path('admin/', admin.site.urls),

    # 로그인
    path('', include('allauth.urls')),
    path('registration/', include('rest_auth.registration.urls')),
    path('', include('rest_auth.urls')),
    url(r'registration/confirm-email/(?P<key>.+)/$', confirm_email, name='confirm_email'),
    path('', include('django.contrib.auth.urls')),


    # 소셜로그인
    path('user/login/kakao/', kakao_login, name='kakao_login'),
    path('user/login/kakao/callback/', kakao_callback, name='kakao_callback'),
 #   path('user/login/kakao/todjango/', KakaoToDjangoLogin.as_view(), name='kakao_todjango_login'),
]