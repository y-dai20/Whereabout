from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager

class BaseQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, **kwargs)
    
    def inactive(self, **kwargs):
        return self.filter(is_deleted=True, **kwargs)
class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQueryset(self.model, using=self._db)

    def get_or_none(self, **kwargs):
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None
    
    def active(self, **kwargs):
        return self.get_queryset().active(**kwargs)
    
    def inactive(self, **kwargs):
        return self.get_queryset().inactive(**kwargs)


class UserQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)
    
    def inactive(self, **kwargs):
        return self.filter(is_active=False, **kwargs)
class UserManager(BaseUserManager, BaseManager):
    def get_queryset(self):
        return UserQueryset(self.model, using=self._db)

    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class ProfileQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, user__is_active=True, **kwargs)
class ProfileManager(BaseManager):
    def get_queryset(self):
        return ProfileQueryset(self.model, using=self._db)


class PostQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(Q(room=None) | Q(room__is_deleted=False), is_deleted=False, user__is_active=True, **kwargs)
class PostManager(BaseManager):
    def get_queryset(self):
        return PostQueryset(self.model, using=self._db)


class ReplyPostQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, user__is_active=True, post__is_deleted=False, **kwargs)
class ReplyPostManager(BaseManager):
    def get_queryset(self):
        return ReplyPostQueryset(self.model, using=self._db)


class ReplyReplyQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, user__is_active=True, reply__is_deleted=False, **kwargs)
class ReplyReplyManager(BaseManager):
    def get_queryset(self):
        return ReplyReplyQueryset(self.model, using=self._db)


class RoomQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, admin__is_active=True, **kwargs)
    def public(self, **kwargs):
        return self.filter(is_public=True, **kwargs)
    def private(self, **kwargs):
        return self.filter(is_public=False, **kwargs)
class RoomManager(BaseManager):
    def get_queryset(self):
        return RoomQueryset(self.model, using=self._db)


class RoomUserQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, room__is_deleted=False, user__is_active=True, **kwargs)
class RoomUserManager(BaseManager):
    def get_queryset(self):
        return RoomUserQueryset(self.model, using=self._db)


class RoomGuestQueryset(models.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_deleted=False, room__is_deleted=False, guest__is_active=True, **kwargs)
class RoomGuestManager(BaseManager):
    def get_queryset(self):
        return RoomGuestQueryset(self.model, using=self._db)