from django.db import models
from django.conf import settings


from base.models import create_id
from base.models.post_models import Post
from base.models.functions import img_directory_path
from base.models.general_models import ObjectExpansion
from base.models.general_models import BaseManager

class ReplyPosition(models.TextChoices):
    AGREE = 'Agree', '賛成'
    NEUTRAL = 'Neutral', '中立'
    DISAGREE = 'Disagree', '反対'

class ReplyPost(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    text = models.CharField(default='', max_length=255, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expansion = models.ForeignKey(ObjectExpansion, on_delete=models.CASCADE)
    url = models.CharField(null=True, blank=True, max_length=255)
    img = models.ImageField(null=True, blank=True, upload_to=img_directory_path)
    position = models.CharField(default=ReplyPosition.NEUTRAL, choices=ReplyPosition.choices, max_length=16)
    type = models.CharField(max_length=8)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ReplyReply(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    text = models.CharField(default='', max_length=255, blank=False)
    reply = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expansion = models.ForeignKey(ObjectExpansion, on_delete=models.CASCADE)
    img = models.ImageField(null=True, blank=True, upload_to=img_directory_path)
    position = models.CharField(choices=ReplyPosition.choices, max_length=16)
    type = models.CharField(max_length=8)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ReplyAgree(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class ReplyFavorite(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class ReplyDemagogy(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class Reply2Agree(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_agree = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class Reply2Favorite(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

class Reply2Demagogy(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_true = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(ReplyReply, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

# @receiver(post_save, sender=ReplyPost)
# def create_onetoone(sender, **kwargs):
#     if kwargs['created']:
#         expansion = ObjectExpansion.objects.create()
#         kwargs['instance'].expansion = expansion

# @receiver(post_save, sender=ReplyReply)
# def create_onetoone(sender, **kwargs):
#     if kwargs['created']:
#         expansion = ObjectExpansion.objects.create()
#         kwargs['instance'].expansion = expansion