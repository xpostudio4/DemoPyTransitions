from __future__ import absolute_import, unicode_literals
from celery import task
from main.models import User
from organizations.models import Organization
from celery.contrib import rdb
import logging

logger = logging.getLogger()
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s [%(lineno)d]')

# StreamHandler
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)


@task(name='invite_user_task')
def invite_user_task(email, sender_username, *args, **kwargs):
    # print('from task')
    logger.log('*************from task**************')
    rdb.set_trace()
    user = invitation_backend().invite_by_email(
            email,
            **{'domain': {'domain': 'localhost:8000'},
                'organization': Organization.objects.last(),
                'sender': User.objects.get(username=sender_username)})
