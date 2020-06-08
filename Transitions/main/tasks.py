from __future__ import absolute_import, unicode_literals
from celery import task
from main.models import User
from organizations.models import Organization


@task(name='invite_user_task')
def invite_user_task(email, sender_username):
    user = invitation_backend().invite_by_email(
            email,
            **{'domain': {'domain': 'localhost:8000'},
                'organization': Organization.objects.last(),
                'sender': User.objects.get(username=sender_username)})
