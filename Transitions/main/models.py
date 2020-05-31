from django.contrib.auth.models import AbstractUser
from django.db import models
from transitions import Machine
from transitions.extensions import HierarchicalGraphMachine as Machine

# Create your models here.


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(("Name of User"), blank=True, max_length=255)

    states = [
        {
            'name': 'created'
        },
        {
            'name': 'invitation-accepted'
        },
        {
            'name': 'pre-authenticated'
        },
        {
            'name': 'authenticated',
            'children': [
                'active',
                'inactive',
                'title-revoked'
            ]
        },
        {
            'name': 'archived'
        }
    ]

    max_tries = 3

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self.try_counter = 0
        self.machine = Machine(
            model=self,
            states=User.states,
            initial='created'
        )

        self.machine.add_transition(
            trigger='accept_invitation',
            source='created',
            dest='invitation-accepted'
        )

        self.machine.add_transition(
            trigger='first_sign_in',
            source='invitation-accepted',
            dest='pre-authenticated'
        )

        self.machine.add_transition(
            trigger='authentication_fail',
            source='pre-authenticated',
            dest='pre-authenticated',
            conditions=['exceeded_tries']
        )

        self.machine.add_transition(
            trigger='authentication_fail',
            source='pre-authenticated',
            dest='archived'
        )

        self.machine.add_transition(
            trigger='authentication_success',
            source='pre-authenticated',
            dest='authenticated_active'
        )

        self.machine.add_transition(
            trigger='set_inactive',
            source='authenticated_active',
            dest='authenticated_inactive'
        )

        self.machine.add_transition(
            trigger='set_active',
            source='authenticated_inactive',
            dest='authenticated_active'
        )

        self.machine.add_transition(
            trigger='revoke_title',
            source=['authenticated_inactive', 'authenticated_active'],
            dest='authenticated_title-revoked'
        )

        self.machine.add_transition(
            trigger='archive_user',
            source='authenticated_title-revoked',
            dest='archived'
        )

    @property
    def exceeded_tries(self):
        self.try_counter += 1
        if self.try_counter > User.max_tries:
            return False
        return True
