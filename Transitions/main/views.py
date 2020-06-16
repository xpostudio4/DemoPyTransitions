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
from rest_framework.decorators import MethodMapper
import logging
logger = logging.getLogger()

class MainView(TemplateView):
    template_name = 'base.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'base.html')

        if request.user.is_authenticated and not request.user.is_superuser:
            return render(request, 'user.html')

        return render(request, self.template_name)

    def post(self, request):
        return render(request, 'base.html')


class DispatcherMixin(viewsets.ModelViewSet):

    def get_action_and_context_from_request(self, request):

        context = request.data['context']
        action = request.data['action']
        
        return action, context

    def dispatch_action(self, request, pk=None, *args, **kwargs):

        # TODO: Log enter and exit from this method
        # TODO: Validate this action is for 'patch' method
        
        action, context = self.get_action_and_context_from_request(request)

        # TODO: Check context is syntactically valid for action

        model_class = self.serializer_class.Meta.model
        
        # TODO: Enter and exit from dispatcher
        success, message = model_class.dispatcher(context, action, pk)
        
        if not success:
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST )

        return Response({'message': message}, status=status.HTTP_200_OK)

    # POST method is handle by the create method
    def create(self, request, *args, **kwargs):
        return self.dispatch_action(request, *args, **kwargs)

    # PUT method is handle by the eupdate method
    def update(self, request, pk, *args, **kwargs):
        return self.dispatch_action(request, pk, *args, **kwargs)

    # PATCH method is handle by the partial_update method
    def partial_update(self, request, pk, *args, **kwargs):
        return self.dispatch_action(request, pk, *args, **kwargs)

    # DELETE method is handle by the delete method
    def delete(self, request, pk, *args, **kwargs):
        return self.dispatch_action(request, pk, *args, **kwargs)


class UserViewSet(DispatcherMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.exclude(user_state='archived')
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )
    model_pk = 'users_pk'

    def __init__(self, *args, **kwargs):
        super(UserViewSet, self).__init__(*args, **kwargs)
        
    def get_queryset(self):
        queryset = User.objects.exclude(user_state='archived')

        pre_auth = self.request.query_params.get('pre_auth', None) == 'true'
        if pre_auth:
            queryset = queryset.filter(user_state='pre-authenticated')
        return queryset

