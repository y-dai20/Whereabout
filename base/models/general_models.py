from django.db import models
from django.conf import settings


from base.models import create_id
import base.models.managers as m

class Personal(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    web = models.CharField(default='', max_length=255, blank=True)
    phone = models.CharField(default='', max_length=15, blank=True)
    zip_code = models.CharField(default='', max_length=8, blank=True)
    state = models.CharField(default='', max_length=15, blank=True)
    city = models.CharField(default='', max_length=15, blank=True)
    address_1 = models.CharField(default='', max_length=15, blank=True)
    address_2 = models.CharField(default='', max_length=15, blank=True)
    mon_from = models.CharField(default='', max_length=5, blank=True)
    mon_to = models.CharField(default='', max_length=5, blank=True)
    tue_from = models.CharField(default='', max_length=5, blank=True)
    tue_to = models.CharField(default='', max_length=5, blank=True)
    wed_from = models.CharField(default='', max_length=5, blank=True)
    wed_to = models.CharField(default='', max_length=5, blank=True)
    thu_from = models.CharField(default='', max_length=5, blank=True)
    thu_to = models.CharField(default='', max_length=5, blank=True)
    fri_from = models.CharField(default='', max_length=5, blank=True)
    fri_to = models.CharField(default='', max_length=5, blank=True)
    sat_from = models.CharField(default='', max_length=5, blank=True)
    sat_to = models.CharField(default='', max_length=5, blank=True)
    sun_from = models.CharField(default='', max_length=5, blank=True)
    sun_to = models.CharField(default='', max_length=5, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Tag(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    name = models.CharField(max_length=15, blank=False, null=False, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
    
class TagSequence(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    tag1 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag1')
    tag2 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag2')
    tag3 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag3')
    tag4 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag4')
    tag5 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag5')
    tag6 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag6')
    tag7 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag7')
    tag8 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag8')
    tag9 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag9')
    tag10 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='tag10')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)