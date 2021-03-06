# Generated by Django 3.0.6 on 2020-06-01 21:37

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20200601_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name of User')),
                ('user_state', models.CharField(choices=[('created', 'Created'), ('pre-authenticated', 'Pre-Authentication'), ('invitation-accepted', 'Invitation Accepted'), ('authentication_active', 'Active'), ('authentication_inactive', 'Inactive'), ('authentication_title-revoked', 'Title Revoked'), ('archived', 'Archived')], default='created', help_text='User state', max_length=32)),
            ],
            bases=(main.models.UserMachineMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_state',
            field=models.CharField(choices=[('created', 'Created'), ('pre-authenticated', 'Pre-Authentication'), ('invitation-accepted', 'Invitation Accepted'), ('authentication_active', 'Active'), ('authentication_inactive', 'Inactive'), ('authentication_title-revoked', 'Title Revoked'), ('archived', 'Archived')], default='created', help_text='User state', max_length=32),
        ),
    ]
