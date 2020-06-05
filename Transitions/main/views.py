from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.mail import send_mail
# Create your views here.
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from main.models import User
from main.serializers import UserSerializer, InviteSerializer
from rest_framework.permissions import AllowAny
import smtplib
from organizations.backends import invitation_backend
from organizations.models import Organization


class MainView(TemplateView):
    template_name = 'base.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'admin.html')

        if request.user.is_authenticated and not request.user.is_superuser:
            return render(request, 'user.html')

        return render(request, self.template_name)

    def post(self, request):
        return render(request, 'base.html')


class TestView(TemplateView):
    def get(self, request):
        return JsonResponse({'message': 'Hello from the other side'})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.exclude(user_state='archived')

    serializer_class = UserSerializer

    permission_classes = (AllowAny, )

    def __init__(self, *args, **kwargs):
        super(UserViewSet, self).__init__(*args, **kwargs)
        self.patch_actions = {
            'pre_auth': self.pre_auth,
            'auth': self.auth,
        }

    def get_queryset(self):
        queryset = User.objects.exclude(user_state='archived')

        pre_auth = self.request.query_params.get('pre_auth', None) == 'true'
        if pre_auth:
            queryset = queryset.filter(user_state='pre-authenticated')
        return queryset

    def create(self, request, *args, **kwargs):
        user = invitation_backend().invite_by_email(
                    request.data['email'],
                    **{'domain': {'domain': 'localhost:8000'},
                        'organization': Organization.objects.last()})
        return Response({'message': 'Ok'}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        return self.patch_actions[request.data['action']](request)

    def delete(self, request, *args, **kwargs):
        user_data = request.data
        user = User.objects.get(email=user_data['email'])
        user.archive_user(user.machine)
        user.save()
        return Response({'message': 'User deleted'}, status=status.HTTP_200_OK)

    def pre_auth(self, request):
        user_data = request.data['context']
        if user_data['password'] != user_data['confirm_password']:
            return Response({'message': 'Pre-auth'}, status=status.HTTP_409_CONFLICT)
        user = User.objects.get(email=user_data['email'])
        user.username = user_data['username']
        user.password = user_data['username']
        user.first_sign_in(user.machine)
        user.save()
        return Response({'message': 'Pre-auth'}, status=status.HTTP_200_OK)

    def auth(self, request):
        user_data = request.data['context']
        user = User.objects.get(email=user_data['email'])
        user.authentication_success(user.machine)
        user.save()
        return Response({'message': 'user is authenticated'}, status=status.HTTP_200_OK)
