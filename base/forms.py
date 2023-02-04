from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from base.models import Post, ReplyPost, ReplyReply
from base.models.room_models import Room, RoomRequestInformation
from base.models.account_models import Profile


EMAIL_MAX_LENGTH = 255
USERNAME_MAX_LENGTH = 50
PROFESSION_MAX_LENGTH = 255
DESCRIPTION_MAX_LENGTH = 255
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 255
POST_TITLE_MAX_LENGTH = 50
POST_TEXT_MAX_LENGTH = 255
REPLY_TEXT_MAX_LENGTH = 255
SOURCE_MAX_LENGTH = 255
ROOM_TITLE_MAX_LENGTH = 50
ROOM_SUBTITLE_MAX_LENGTH = 255
ROOM_INFORMATION_MAX_LENGTH = 255
IMAGE_EXTENSION = "jpg|jpeg|png|ico|bmp"
VIDEO_EXTENSION = "mp4"

class ValidationForm:
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if USERNAME_MAX_LENGTH < len(username):
            raise ValidationError(('ユーザー名は{}文字以下で入力してください'.format(USERNAME_MAX_LENGTH)))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        if EMAIL_MAX_LENGTH < len(email):
            raise ValidationError(('メールアドレスは{}文字以下で入力してください'.format(EMAIL_MAX_LENGTH)))
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if PASSWORD_MIN_LENGTH > len(password) or PASSWORD_MAX_LENGTH < len(password):
            raise ValidationError(('パスワードは{}文字以上{}文字以下で入力してください'.format(PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)))
        return password

    def clean_source(self):
        source = self.cleaned_data.get('source')

        if source is not None and SOURCE_MAX_LENGTH < len(source):
            raise ValidationError(('ソースは{}文字以下で入力してください'.format(SOURCE_MAX_LENGTH)))
        return source


class SignUpForm(ValidationForm, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password', )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ChangePasswordForm(ValidationForm, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('password',)

class SendMailForm(ValidationForm, forms.Form):
    email = forms.CharField(max_length=EMAIL_MAX_LENGTH, required=True)

class UserProfileForm(ValidationForm, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('img', 'profession', 'description', )
    
    def clean_profession(self):
        profession = self.cleaned_data.get('profession')
        if PROFESSION_MAX_LENGTH < len(profession):
            raise ValidationError(('職業は{}文字以下で入力してください'.format(PROFESSION_MAX_LENGTH)))
        return profession

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if DESCRIPTION_MAX_LENGTH < len(description):
            raise ValidationError(('詳細は{}文字以下で入力してください'.format(DESCRIPTION_MAX_LENGTH)))
        return description

class PostForm(ValidationForm, forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ('title', 'text', 'source', )
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if POST_TITLE_MAX_LENGTH < len(title):
            raise ValidationError(('タイトルは{}文字以下で入力してください'.format(POST_TITLE_MAX_LENGTH)))
        return title
        
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if POST_TEXT_MAX_LENGTH < len(text):
            raise ValidationError(('本文は{}文字以下で入力してください'.format(POST_TEXT_MAX_LENGTH)))
        return text

class ReplyForm(ValidationForm, forms.ModelForm):

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if REPLY_TEXT_MAX_LENGTH < len(text):
            raise ValidationError(('本文は{}文字以下で入力してください'.format(REPLY_TEXT_MAX_LENGTH)))
        return text

class ReplyPostForm(ReplyForm):
    
    class Meta:
        model = ReplyPost
        fields = ('text', 'source', 'type', )

class ReplyReplyForm(ReplyForm):
    
    class Meta:
        model = ReplyReply
        fields = ('text', 'source', 'type', )

class CreateRoomForm(ValidationForm, forms.ModelForm):

    class Meta:
        model = Room
        fields = ('title', 'subtitle', 'is_public', 'need_approval')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if ROOM_TITLE_MAX_LENGTH < len(title):
            raise ValidationError(('タイトルは{}文字以下で入力してください'.format(ROOM_TITLE_MAX_LENGTH)))
        return title

    def clean_subtitle(self):
        subtitle = self.cleaned_data.get('subtitle')
        if ROOM_SUBTITLE_MAX_LENGTH < len(subtitle):
            raise ValidationError(('サブタイトルは{}文字以下で入力してください'.format(ROOM_SUBTITLE_MAX_LENGTH)))
        return subtitle

class UpdateRoomForm(CreateRoomForm):

    class Meta:
        model = Room
        fields = ('title', 'subtitle')

class RoomRequestInformationForm(ValidationForm, forms.ModelForm):

    class Meta:
        model = RoomRequestInformation
        fields = ('title', 'type', 'choice', 'min_length', 'max_length')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if ROOM_INFORMATION_MAX_LENGTH < len(title):
            raise ValidationError(('タイトルは{}文字以下で入力してください'.format(ROOM_INFORMATION_MAX_LENGTH)))
        return title

    def clean_type(self):
        _type = self.cleaned_data.get('type')
        if ROOM_INFORMATION_MAX_LENGTH < len(_type):
            raise ValidationError('文字数が異常です')
        return _type

    def clean_choice(self):
        choice = self.cleaned_data.get('choice')
        if ROOM_INFORMATION_MAX_LENGTH < len(choice):
            raise ValidationError('文字数が異常です')
        return choice
    
    def clean_min_length(self):
        min_length = self.cleaned_data.get('min_length')
        if 0 > min_length:
            raise ValidationError('最小文字数は1文字です')
        return min_length

    def clean_max_length(self):
        max_length = self.cleaned_data.get('max_length')
        if ROOM_INFORMATION_MAX_LENGTH < max_length:
            raise ValidationError(('最大文字数は{}です'.format(ROOM_INFORMATION_MAX_LENGTH)))
        return max_length