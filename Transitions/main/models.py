from django.contrib.auth.models import AbstractUser
from django.db import models
from transitions import Machine
from transitions.extensions import GraphMachine as Machine

# Create your models here.


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(("Name of User"), blank=True, max_length=255)
    states = [
        'created',
        'invitation_accepted',
        'pre-authenticated',
        'authenticated/active',
        'inactive',
        'title_revoked',
        'archived'
    ]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.machine = Machine(
            model=self,
            states=User.states,
            initial='created'
        )

        self.machine.add_transition(
            trigger='accept_invitation',
            source='created',
            dest='invitation_accepted'
        )

        self.machine.add_transition(
            trigger='first_sign_in',
            source='invitation_accepted',
            dest='pre-authenticated'
        )

        self.machine.add_transition(
            trigger='authentication_fail',
            source='pre-authenticated',
            dest='pre-authenticated'
        )

        self.machine.add_transition(
            trigger='authentication_success',
            source='pre-authenticated',
            dest='authenticated/active'
        )

        self.machine.add_transition(
            trigger='set_active',
            source='authenticated/active',
            dest='inactive'
        )

        self.machine.add_transition(
            trigger='set_inactive',
            source='inactive',
            dest='authenticated/active'
        )

        self.machine.add_transition(
            trigger='revoke_title',
            source=['inactive', 'authenticated/active'],
            dest='title_revoked'
        )

        self.machine.add_transition(
            trigger='archive_user',
            source='title_revoked',
            dest='archived'
        )
