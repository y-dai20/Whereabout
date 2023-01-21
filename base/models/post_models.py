from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.models import create_id
from base.models.functions import post_directory_path, video_directory_path
from base.models.room_models import Room
from base.models.general_models import ObjectExpansion

class Post(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=50, blank=False)
    text = models.CharField(default='', max_length=255, blank=False)
    video = models.FileField(null=True, blank=True, upload_to=video_directory_path)
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expansion = models.ForeignKey(ObjectExpansion, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class PostImgs(models.Model):
    post = models.OneToOneField(Post, primary_key=True, on_delete=models.CASCADE)
    img1 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img2 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img3 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)
    img4 = models.ImageField(null=True, blank=True, upload_to=post_directory_path)

    def __str__(self):
        return self.post

class PostAgree(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class PostFavorite(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class PostDemagogy(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj