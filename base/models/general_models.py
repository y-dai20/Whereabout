from django.db import models
from django.conf import settings


from base.models import create_id

class BaseManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None

class ObjectExpansion(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    agree_count = models.IntegerField(default=0)
    disagree_count = models.IntegerField(default=0)
    true_count = models.IntegerField(default=0)
    false_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)