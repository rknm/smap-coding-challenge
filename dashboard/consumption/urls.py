from django.conf.urls import url
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from .views import UserDataViewSet, OtherDataViewSet

router = DefaultRouter()
router.register('userdata', UserDataViewSet)
router.register('otherdata', OtherDataViewSet)

urlpatterns = [
    url(r'^$', views.summary),
    url(r'^summary/', views.summary),
    url(r'^detail/', views.detail),
    path('api/', include(router.urls)),
]
