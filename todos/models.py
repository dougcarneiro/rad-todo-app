from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid

class Todo(models.Model):
    class Priority(models.TextChoices):
        HIGH = 'HIGH', _('High')
        MEDIUM = 'MEDIUM', _('Medium')
        LOW = 'LOW', _('Low')
        NORMAL = 'NORMAL', _('Normal')

    class Status(models.TextChoices):
        DONE = 'DONE', _('Done')
        PENDING = 'PENDING', _('Pending')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos', verbose_name=_('user'))
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    priority = models.CharField(_('priority'), max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(_('status'), max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    due_date = models.DateField(_('due date'), blank=True, null=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    removed = models.BooleanField(_('removed'), default=False)

    def __str__(self):
        return self.title
