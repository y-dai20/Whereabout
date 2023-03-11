from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from base.models import create_id


from base.models.functions import img_directory_path
from base.models.general_models import BaseManager, Tag, TagSequence

class UserManager(BaseUserManager, BaseManager):
 
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
 
class Guest(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    email = models.EmailField(max_length=255, unique=True)
    access_count = models.IntegerField(default=0)
    one_time_id = models.CharField(max_length=128)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class UserReset(models.Model):
    objects = UserManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prev_password = models.CharField(max_length=128)
    one_time_id = models.CharField(max_length=128)
    is_success = models.BooleanField(null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class User(AbstractBaseUser):
    objects = UserManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    username = models.CharField(max_length=255, unique=True, blank=True, default='匿名')
    email = models.EmailField(max_length=255, unique=True)
    point = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    fail_login_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', ]
 
    def __str__(self):
        return self.username
 
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
 
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
 
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        ordering = ['-created_at']

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    img = models.ImageField(null=True, blank=True, upload_to=img_directory_path)
    profession = models.CharField(default='', blank=True, max_length=255)
    description = models.CharField(default='', blank=True, max_length=255)
    tag_sequence = models.ForeignKey(TagSequence, on_delete=models.CASCADE, null=True)
    followed_count = models.IntegerField(default=0)
    blocked_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class UserEvaluate(models.Model):
    objects = UserManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    false_access = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class UserFollow(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower')
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followee')    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserBlock(models.Model):
    objects = BaseManager()
    id = models.CharField(default=create_id, primary_key=True, max_length=settings.ID_LENGTH)
    blocker =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocker')
    blockee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blockee')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# OneToOneFieldを同時に作成
@receiver(post_save, sender=User)
def create_onetoone(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])