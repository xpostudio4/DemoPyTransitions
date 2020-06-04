from django.contrib import admin
from django.urls import path, include
from main.views import MainView, TestView, UserViewSet
from rest_framework_nested import routers
from organizations.backends import invitation_backend

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path("", MainView.as_view(), name='main'),
    path('test/', TestView.as_view()),
    path(r'^accounts/', include('organizations.urls')),
    path(r'^invitations/', include(invitation_backend().get_urls())),
]
