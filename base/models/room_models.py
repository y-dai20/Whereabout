from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from base.models import create_id
from base.models.general_models import BaseManager, Personal, Tag, TagSequence
from base.models.functions import room_directory_path, video_directory_path


class RoomAuthority(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    can_reply = models.BooleanField(default=False)
    can_post = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#todo (中) 関連するRoomの情報を付与
#todo (中) 文字数の見直し
class Room(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=255, blank=False)
    subtitle = models.CharField(default='', max_length=255, blank=False)
    point = models.IntegerField(default=0)
    video = models.FileField(null=True, blank=True, upload_to=video_directory_path)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    need_approval = models.BooleanField(default=False)
    authority = models.ForeignKey(RoomAuthority, on_delete=models.PROTECT)
    personal = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True)
    tag_sequence = models.ForeignKey(TagSequence, on_delete=models.CASCADE, null=True)
    img1 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img2 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img3 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img4 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    img5 = models.ImageField(null=True, blank=True, upload_to=room_directory_path)
    good_count = models.IntegerField(default=0)
    bad_count = models.IntegerField(default=0)
    participant_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'NAME:{}_ID:{}'.format(self.title, self.id)
    
    class Meta:
        ordering = ['-created_at']

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

class RoomTab(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='title', max_length=32, blank=False, null=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RoomTabSequence(models.Model):
    room = models.OneToOneField(Room, primary_key=True, on_delete=models.CASCADE)
    tab1 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab1")
    tab2 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab2")
    tab3 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab3")
    tab4 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab4")
    tab5 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab5")
    tab6 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab6")
    tab7 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab7")
    tab8 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab8")
    tab9 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab9")
    tab10 = models.ForeignKey(RoomTab, null=True, on_delete=models.SET_NULL, related_name="tab10")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RoomTabItem(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH, editable=False)
    title = models.CharField(default='', max_length=255, blank=True)
    text = models.CharField(default='', max_length=1024, blank=True)
    img = models.ImageField(default='', blank=True, upload_to=room_directory_path)
    row = models.IntegerField(null=False, blank=False)
    column = models.IntegerField(null=False, blank=False)
    col = models.IntegerField(null=False, blank=False)
    room_tab = models.ForeignKey(RoomTab, on_delete=models.CASCADE, default=None)
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
    updated_at = models.DateTimeField(auto_now=True)

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
    authority = models.ForeignKey(RoomAuthority, on_delete=models.PROTECT, default=None)
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

@receiver(post_save, sender=Room)
def create_onetoone(sender, **kwargs):
    if kwargs['created']:
        RoomTabSequence.objects.create(room=kwargs['instance'])
        RoomReplyType.objects.create(room=kwargs['instance'])