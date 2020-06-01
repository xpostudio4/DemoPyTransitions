from django.contrib.auth.models import AbstractUser
from django.db import models
from transitions import Machine
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions import MachineFactory
from django_transitions.workflow import StatusBase
from django_transitions.workflow import StateMachineMixinBase

# Create your models here.


class UserStatus(StatusBase):
    # STATES
    CREATED = 'created'
    PRE_AUTH = 'pre-authenticated'
    INV_ACCEPTED = 'invitation-accepted'
    AUTH_ACTIVE = 'authentication_active'
    AUTH_INACTIVE = 'authentication_inactive'
    AUTH_REVOKED = 'authentication_title-revoked'
    ARCHIVED = 'archived'

    # TRANSITIONS
    ACCEPT = 'accept_invitation'
    SIGN = 'first_sign_in'
    AUTH_FAIL = 'authentication_fail'
    AUTH_SUCCESS = 'authentication_success'
    SET_INACTIVE = 'set_inactive'
    SET_ACTIVE = 'set_active'

    SM_INITIAL_STATE = PRE_AUTH

    SM_STATES = [
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

    SM_STATES_OLD = [
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

    TRANSITION_LABELS = {
        ACCEPT: {'label': 'Accept Invitation'},
        SIGN: {'label': 'First sign in'},
        AUTH_FAIL: {'label': 'Authentication Fail'},
        AUTH_SUCCESS: {'label': 'Authentication Success'},
        SET_INACTIVE: {'label': 'Set Inactive'},
        SET_ACTIVE: {'label': 'Set Active'},
    }

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
        auto_transitions=False,
        **status_class.get_kwargs()
    )

    @property
    def state(self):
        """Get the items workflowstate or the initial state if none is set."""
        if self.user_state:
            return self.user_state
        return self.machine.initial

    @state.setter
    def state(self, value):
        """Set the items workflow state."""
        self.user_state = value
        return self.user_state

    def get_wf_graph(self):
        """Get the graph for this machine."""
        diagram_cls = MachineFactory.get_predefined(graph=True, nested=True)
        machine = diagram_cls(
            model=self,
            auto_transitions=False,
            title=type(self).__name__,
            **self.status_class.get_kwargs()  # noqa: C815
        )
        return machine.get_graph()


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
