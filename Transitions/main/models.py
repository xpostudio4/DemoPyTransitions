from django.contrib.auth.models import AbstractUser
from django.db import models
from transitions import Machine
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions import MachineFactory
from django_transitions.workflow import StatusBase
from django_transitions.workflow import StateMachineMixinBase

# Create your models here.


class UserStatus(StatusBase):

    CREATED = 'created'
    PRE_AUTH = 'pre-authenticated'
    INV_ACCEPTED = 'invitation-accepted'
    AUTH_ACTIVE = 'authentication_active'
    AUTH_INACTIVE = 'authentication_inactive'
    AUTH_REVOKED = 'authentication_title-revoked'
    ARCHIVED = 'archived'

    SM_INITIAL_STATE = CREATED

    SM_STATES_OLD = [
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

    SM_STATES = [
        CREATED,
        PRE_AUTH,
        INV_ACCEPTED,
        AUTH_ACTIVE,
        AUTH_INACTIVE,
        AUTH_REVOKED,
        ARCHIVED,
    ]

    STATE_CHOICES = (
        (CREATED, 'Created'),
        (PRE_AUTH, 'Pre-Authentication'),
        (INV_ACCEPTED, 'Invitation Accepted'),
        (AUTH_ACTIVE, 'Active'),
        (AUTH_INACTIVE, 'Inactive'),
        (AUTH_REVOKED, 'Title Revoked'),
        (ARCHIVED, 'Archived'),
    )

    SM_TRANSITIONS = [
        {
            'trigger': 'accept_invitation',
            'source': 'created',
            'dest': 'invitation-accepted'
        },
        {
            'trigger': 'first_sign_in',
            'source': 'invitation-accepted',
            'dest': 'pre-authenticated'
        },
        {
            'trigger': 'authentication_fail',
            'source': 'pre-authenticated',
            'dest': 'pre-authenticated',
            # 'conditions': ['exceeded_tries']
        },
        {
            'trigger': 'authentication_fail',
            'source': 'pre-authenticated',
            'dest': 'archived'
        },
        {
            'trigger': 'authentication_success',
            'source': 'pre-authenticated',
            'dest': 'authenticated_active'
        },
        {
            'trigger': 'set_inactive',
            'source': 'authenticated_active',
            'dest': 'authenticated_inactive'
        },
        {
            'trigger': 'set_active',
            'source': 'authenticated_inactive',
            'dest': 'authenticated_active'
        }
    ]

# self.machine.add_transition(
#             trigger='revoke_title',
#             source=['authenticated_inactive', 'authenticated_active'],
#             dest='authenticated_title-revoked'
#         )

#         self.machine.add_transition(
#             trigger='archive_user',
#             source='authenticated_title-revoked',
#             dest='archived'
#         )


class UserMachineMixin(StateMachineMixinBase):
    status_class = UserStatus

    machine = Machine(
        model=None,
        **status_class.get_kwargs()
    )

    @property
    def main_state(self):
        """Get the items workflowstate or the initial state if none is set."""
        if self.user_state:
            return self.user_state
        return self.machine.initial

    @main_state.setter
    def main_state(self, value):
        """Set the items workflow state."""
        self.user_state = value
        return self.user_state


class User(UserMachineMixin, AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(("Name of User"), blank=True, max_length=255)

    # MAX_TRIES = 3
    user_state = models.CharField(
        null=False,
        blank=False,
        default=UserStatus.SM_INITIAL_STATE,
        choices=UserStatus.STATE_CHOICES,
        max_length=32,
        help_text='User state',
    )


class UserModel(UserMachineMixin, models.Model):
    name = models.CharField(("Name of User"), blank=True, max_length=255)

    user_state = models.CharField(
        null=False,
        blank=False,
        default=UserStatus.SM_INITIAL_STATE,
        choices=UserStatus.STATE_CHOICES,
        max_length=32,
        help_text='User state',
    )
