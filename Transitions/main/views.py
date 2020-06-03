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
    template_name = 'index.html'
    
    def get(self, request):
        if request.user.is_authenticated and request.user.is_admin:
            return render(request, 'admin.html')
        
        if request.user.is_authenticated and not request.user.is_admin:
            return render(request, 'user.html')
        
        return render(request, self.template_name)
        

    def post(self, request):
        return render(request, 'index.html')


class TestView(TemplateView):
    def get(self, request):
        return JsonResponse({'message': 'Hello from the other side'})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InviteViewSet(viewsets.ViewSet):
    serializer_class = InviteSerializer

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        print(request)
        user = invitation_backend().invite_by_email(
                    request.data['email'],
                    **{'domain': 'http://localhost:8000/',
                        'organization': Organization.objects.last()})
        return Response({'message': 'Ok'}, status=status.HTTP_200_OK)
