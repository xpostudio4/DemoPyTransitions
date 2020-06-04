from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader
from django.utils.translation import ugettext as _
from django import forms

from organizations.backends.defaults import InvitationBackend
from organizations.backends.forms import UserRegistrationForm
from organizations.backends.forms import org_registration_form
from organizations.backends.tokens import RegistrationTokenGenerator
from organizations.compat import reverse
from organizations.utils import create_organization
from organizations.utils import default_org_model
from organizations.utils import model_field_attr


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=30,
                                       widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password != password_confirm or not password:
            raise forms.ValidationError(_("Your password entries must match"))
        return super(RegistrationForm, self).clean()

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_superuser', 'is_active', 'last_login',
                   'date_joined', 'groups', 'user_permissions', 'user_state',
                   'first_name', 'last_name', 'name')


class MesosInvitationBackend(InvitationBackend):
    form_class = RegistrationForm

    def __init__(self, *args, **kwargs):
        super(MesosInvitationBackend, self).__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse('success_view')

    def activate_view(self, request, user_id, token):
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
            user.accept_invitation(user.machine)
            user.save()
        except self.user_model.DoesNotExist:
            raise Http404(_("Your URL may have expired."))

        return render(request, 'user.html')
