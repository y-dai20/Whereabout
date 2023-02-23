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

class Personal(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    web = models.CharField(default='', max_length=255, blank=True)
    phone = models.CharField(default='', max_length=15, blank=True)
    zip_code = models.CharField(default='', max_length=7, blank=True)
    state = models.CharField(default='', max_length=15, blank=True)
    city = models.CharField(default='', max_length=15, blank=True)
    address_1 = models.CharField(default='', max_length=15, blank=True)
    address_2 = models.CharField(default='', max_length=15, blank=True)
    mon = models.CharField(default='', max_length=15, blank=True)
    tue = models.CharField(default='', max_length=15, blank=True)
    wed = models.CharField(default='', max_length=15, blank=True)
    thu = models.CharField(default='', max_length=15, blank=True)
    fri = models.CharField(default='', max_length=15, blank=True)
    sat = models.CharField(default='', max_length=15, blank=True)
    sun = models.CharField(default='', max_length=15, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)