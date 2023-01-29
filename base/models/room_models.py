from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from base.models import create_id
from base.models.general_models import BaseManager
from base.models.functions import room_directory_path, video_directory_path


class RoomAuthority(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    can_reply = models.BooleanField(default=False)
    can_post = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#todo (高) 関連するRoomの情報を付与
class Room(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=255, blank=False)
    subtitle = models.CharField(default='', max_length=255, blank=False)
    video = models.FileField(null=True, blank=True, upload_to=video_directory_path)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    need_approval = models.BooleanField(default=False)
    authority = models.ForeignKey(RoomAuthority, on_delete=models.CASCADE)
    good_count = models.IntegerField(default=0)
    bad_count = models.IntegerField(default=0)
    participant_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'admin'], name="unique_title_user")
        ]
        ordering = ['-created_at']

class RoomImgs(models.Model):
    room = models.OneToOneField(Room, primary_key=True, on_delete=models.CASCADE)
    img1 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img2 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img3 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img4 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img5 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)

    def __str__(self):
        return self.room

class RoomRequestInformation(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=1)
    title = models.CharField(max_length=255, blank=False)
    type = models.CharField(max_length=255, blank=False)
    choice = models.CharField(max_length=255, blank=True)
    min_length = models.IntegerField(default=0)
    max_length = models.IntegerField(default=255)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RoomInformation(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    rri = models.ForeignKey(RoomRequestInformation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class TabContent(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='title', max_length=32, blank=False, null=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TabPermutation(models.Model):
    room = models.OneToOneField(Room, primary_key=True, on_delete=models.CASCADE)
    tab_content1 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content1")
    tab_content2 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content2")
    tab_content3 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content3")
    tab_content4 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content4")
    tab_content5 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content5")
    tab_content6 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content6")
    tab_content7 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content7")
    tab_content8 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content8")
    tab_content9 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content9")
    tab_content10 = models.ForeignKey(TabContent, null=True, on_delete=models.CASCADE, related_name="tab_content10")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TabContentItem(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=255, blank=True)
    text = models.CharField(default='', max_length=1024, blank=True)
    img = models.ImageField(default='', blank=True, upload_to=room_directory_path)
    row = models.IntegerField(null=False, blank=False)
    column = models.IntegerField(null=False, blank=False)
    col = models.IntegerField(null=False, blank=False)
    tab_content_id = models.ForeignKey(TabContent, on_delete=models.CASCADE, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RoomReplyType(models.Model):
    room = models.OneToOneField(Room, primary_key=True, on_delete=models.CASCADE)
    type1 = models.CharField(default='つぶやき', max_length=8)
    type2 = models.CharField(default='根拠', max_length=8)
    type3 = models.CharField(default='確認', max_length=8)
    type4 = models.CharField(default='要求', max_length=8)
    type5 = models.CharField(default='予想', max_length=8)
    type6 = models.CharField(default='回答', max_length=8)
    type7 = models.CharField(default='質問', max_length=8)
    type8 = models.CharField(default='補足', max_length=8)
    type9 = models.CharField(default='証拠', max_length=8)
    type10 = models.CharField(default='その他', max_length=8)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room

class RoomGuest(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guest")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'guest'], name="unique_room_guest")
        ]

class RoomUser(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    authority = models.ForeignKey(RoomAuthority, on_delete=models.CASCADE, default=None)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'user'], name="unique_room_user")
        ]

class RoomInviteUser(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invite_user")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RoomGood(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    is_good = models.BooleanField(null=False, blank=False)
    obj = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.obj

@receiver(post_save, sender=Room)
def create_onetoone(sender, **kwargs):
    if kwargs['created']:
        TabPermutation.objects.create(room=kwargs['instance'])
        RoomReplyType.objects.create(room=kwargs['instance'])