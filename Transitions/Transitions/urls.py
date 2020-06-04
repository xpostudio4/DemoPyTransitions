from django.contrib import admin
from django.urls import path, include
from main.views import MainView, TestView, UserViewSet, InviteViewSet
from rest_framework_nested import routers
from organizations.backends import invitation_backend

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
# users_router = routers.NestedSimpleRouter(router, r'users', lookup='users')
# router.register(r'invite', InviteViewSet, basename='users-invite')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", MainView.as_view(), name='main'),
    path('test/', TestView.as_view()),
    path('users/invite/', InviteViewSet.as_view({'post': 'post'}), name='invite'),
    path('', include(router.urls)),
    path(r'^invitations/', include(invitation_backend().get_urls())),
    # path('', include(users_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
