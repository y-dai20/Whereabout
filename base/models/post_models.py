from django.db import models
from django.conf import settings


from base.models import create_id
from base.models.functions import post_directory_path, video_directory_path
from base.models.room_models import Room
from base.models.general_models import BaseManager, Tag

class Post(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=50, blank=False)
    text = models.CharField(default='', max_length=255, blank=False)
    source = models.CharField(default='', max_length=255, blank=True)
    video = models.FileField(null=True, blank=True, upload_to=video_directory_path)
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag1 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='post_tag1')
    tag2 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='post_tag2')
    tag3 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='post_tag3')
    tag4 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='post_tag4')
    tag5 = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, related_name='post_tag5')
    img1 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img2 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img3 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img4 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    agree_count = models.IntegerField(default=0)
    disagree_count = models.IntegerField(default=0)
    true_count = models.IntegerField(default=0)
    false_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class PostAgree(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostFavorite(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostDemagogy(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)