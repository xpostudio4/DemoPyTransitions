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

from organizations.backends.defaults import InvitationBackend
from organizations.backends.forms import UserRegistrationForm
from organizations.backends.forms import org_registration_form
from organizations.backends.tokens import RegistrationTokenGenerator
from organizations.compat import reverse
from organizations.utils import create_organization
from organizations.utils import default_org_model
from organizations.utils import model_field_attr


class MesosInvitationBackend(InvitationBackend):

    def __init__(self, *args, **kwargs):
        super(MesosInvitationBackend, self).__init__(*args, **kwargs)

    def activate_view(self, request, user_id, token):
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
            user.accept_invitation(user.machine)
            user.save()
        except self.user_model.DoesNotExist:
            raise Http404(_("Your URL may have expired."))
        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))
        form = self.get_form(data=request.POST or None, files=request.FILES or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            self.activate_organizations(user)
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            login(request, user)
            return redirect(self.get_success_url())

        return render(request, self.registration_form_template, {'form': form})