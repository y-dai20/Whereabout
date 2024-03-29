from django.db import models
from django.conf import settings
from django.urls import reverse

from base.models import create_id
from base.models.post_models import Post
from base.models.functions import img_directory_path
import base.models.managers as m

class ReplyPosition(models.TextChoices):
    AGREE = 'Agree', '賛成'
    NEUTRAL = 'Neutral', '中立'
    DISAGREE = 'Disagree', '反対'

class ReplyPost(models.Model):
    objects = m.ReplyPostManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    text = models.CharField(default='', max_length=255, blank=False)
    source = models.CharField(default='', max_length=255, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agree_count = models.IntegerField(default=0)
    disagree_count = models.IntegerField(default=0)
    true_count = models.IntegerField(default=0)
    false_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    img = models.ImageField(null=True, blank=True, upload_to=img_directory_path)
    position = models.CharField(default=ReplyPosition.NEUTRAL, choices=ReplyPosition.choices, max_length=16)
    type = models.CharField(max_length=8)
    is_accounted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('reply-detail', kwargs={'reply_pk':self.id})

    class Meta:
        ordering = ['-created_at']

class ReplyReply(models.Model):
    objects = m.ReplyReplyManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    text = models.CharField(default='', max_length=255, blank=False)
    source = models.CharField(default='', max_length=255, blank=True)
    reply = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agree_count = models.IntegerField(default=0)
    disagree_count = models.IntegerField(default=0)
    true_count = models.IntegerField(default=0)
    false_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    img = models.ImageField(null=True, blank=True, upload_to=img_directory_path)
    position = models.CharField(default=ReplyPosition.NEUTRAL, choices=ReplyPosition.choices, max_length=16)
    type = models.CharField(max_length=8)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ReplyAgree(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReplyFavorite(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReplyDemagogy(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reply2Agree(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reply2Favorite(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reply2Demagogy(models.Model):
    objects = m.BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)