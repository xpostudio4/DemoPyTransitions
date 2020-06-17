from __future__ import absolute_import, unicode_literals
from celery import task
from organizations.models import Organization
from organizations.backends import invitation_backend
from celery.contrib import rdb
import logging

# logger = logging.getLogger()
# formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s [%(lineno)d]')

# # StreamHandler
# sh = logging.StreamHandler()
# sh.setFormatter(formatter)
# logger.addHandler(sh)


@task(name='invite_user_task')
def invite_user_task(email, *args, **kwargs):
    print('from task')
    # logger.log(msg='*************from task**************')

    org = Organization.objects.last()
    print(f'org: {org}, sender: {sender_username}')

    user = invitation_backend().invite_by_email(
            email,
            **{'domain': {'domain': 'localhost:8000'},
                'organization': Organization.objects.last()})


@task(name='pre_auth')
def pre_auth():
    pass
