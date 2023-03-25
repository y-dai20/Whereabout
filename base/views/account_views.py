from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.views.generic import CreateView, TemplateView, ListView, View
from django.conf import settings
from django.http import JsonResponse, Http404
from django.contrib.auth import login
from django.utils.timezone import make_naive
from django.contrib import messages
from django.shortcuts import render


import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.forms import SignUpForm, ChangePasswordForm, SendMailForm, UserProfileForm
from base.models import Room, RoomGuest, TagSequence
from base.models.room_models import RoomInviteUser, RoomUser, RoomAuthority
from base.models.account_models import User, Guest, UserReset
from base.views.general_views import UserItemView, SendMailView, HeaderView
from base.views.mixins import LoginRequiredMixin

from datetime import timedelta

class LoginView(HeaderView, LoginView):
    template_name = 'pages/login.html'
    max_fail_login_count = 5
    
    #todo (低) login with username, email, password
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        if user is not None and user.fail_login_count > self.max_fail_login_count:
            messages.error(self.request, 'ログイン失敗回数が許容範囲を超えました')
            messages.error(self.request, 'パスワードリセットを試してください')
            return render(self.request, self.template_name)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_user()
        user.fail_login_count = 0
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ユーザー名かパスワードが間違っています')
        
        user = self.get_user()
        if user is not None:
            user.fail_login_count = user.fail_login_count + 1
            user.save()
        return super().form_invalid(form)
    
    def get_user(self):
        return f.get_from_queryset(User.objects.active(username=f.get_dict_item(self.request.POST, 'username')))

class SignUpView(HeaderView, CreateView):
    form_class = SignUpForm
    template_name = 'pages/signup.html'
    registrable_seconds = 10 * 60

    def get(self, request, *args, **kwargs):
        self.guest = self.get_guest()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.guest = self.get_guest()

        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        user = User.objects.get_or_none(email=self.guest.email)
        if user is not None:
            raise MyBadRequest('user is exist.')

        if f.get_diff_seconds_from_now(self.guest.updated_at) > self.registrable_seconds:
            return JsonResponse(f.get_json_error_message(['時間切れです', 'メールアドレスの登録からやり直してください']))

        user = form.save()
        self.guest.is_deleted = True
        self.guest.save()
        
        # adminのRoomに強制参加
        admin = User.objects.get_or_none(username='admin', is_admin=True)
        if admin is not None:
            rooms = Room.objects.active(admin=admin)
            for room in rooms:
                RoomUser.objects.create(
                    room=room,
                    user=user,
                    authority=RoomAuthority.objects.create(
                        can_reply=room.authority.can_reply, 
                        can_post=room.authority.can_post, 
                        is_admin=room.authority.is_admin
                    ),
                )      

        login(request, user)
        return JsonResponse(f.get_json_success_message(['ユーザー登録しました']))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.guest.email
        return context

    def get_guest(self):
        return f.get_object_or_404_from_q(Guest.objects.active(one_time_id=f.get_dict_item(self.kwargs, 'one_time_id')))

class SendMailForSignupView(HeaderView, SendMailView):
    form_class = SendMailForm
    template_name = 'pages/send_mail_for_signup.html'
    mail_title = settings.TITLE + '：ユーザー登録'
    max_access_count = 3
    send_mail_interval = 24 * 60 * 60

    #todo (低) 嫌がらせ対策が必要
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        self.email = form.clean_email()
        user = User.objects.get_or_none(email=self.email)
        if user is not None:
            guest = f.get_object_or_404_from_q(Guest.objects.filter(email=self.email))
            access_count = guest.access_count
            guest.access_count = access_count + 1
            guest.save()
            self.send_mail(self.mail_title, 'このメールアドレスで既にユーザー登録されています', [self.email])
            return self.get_success_json_response()
        
        guest = Guest.objects.get_or_none(email=self.email)
        if guest is None:
            guest = Guest.objects.create(email=self.email, one_time_id=self.get_one_time_id())
            message = self.get_register_message(guest.one_time_id)
            self.send_mail(self.mail_title, message, [self.email])
            return self.get_success_json_response()

        if f.get_diff_seconds_from_now(guest.updated_at) > self.send_mail_interval:
            guest.access_count = 0

        if guest.access_count > self.max_access_count:
            return JsonResponse(f.get_json_error_message([
                '入力したメールアドレスに対してのアクセス回数が許容範囲を超えています', 
                '登録するメールアドレスを変更するか，1日以上の間隔を空けて再度登録してください']))

        access_count = guest.access_count
        guest.access_count = access_count + 1
        guest.one_time_id = self.get_one_time_id()
        guest.is_deleted = False
        guest.save()

        message = self.get_register_message(guest.one_time_id)
        self.send_mail(self.mail_title, message, [self.email])
        return self.get_success_json_response()

    def get_register_message(self, one_time_id):
        return '\
        以下のURLをクリックしてユーザー登録を完了してください．\
        \n{}/signup/{}/\
        \n(期限：5分以内)'.format(self.get_base_path(), one_time_id)

#todo (低) 変更の回数制限は不要？
class ChangePasswordView(LoginRequiredMixin, View):
    form_class = ChangePasswordForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))
        
        user = request.user
        user.password = make_password(form.clean_password())
        user.fail_login_count = 0
        user.save()

        login(request, user)

        return JsonResponse(f.get_json_success_message(['パスワードを変更しました']))

class ResetPasswordBaseView(View):
    resettable_seconds = 5 * 60
    resettable_interval = 10 * 24 * 60 * 60

class ResetPasswordView(ResetPasswordBaseView, TemplateView):
    form_class = ChangePasswordForm
    template_name = 'pages/reset_password.html'

    def get(self, request, *args, **kwargs):
        ur = self.get_user_reset()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ur = self.get_user_reset()
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        if f.get_diff_seconds_from_now(ur.updated_at) > self.resettable_seconds:
            return JsonResponse(f.get_json_error_message(['時間切れです', 'もう一度メール送信からやり直してください']))

        user = ur.user
        ur.prev_password = user.password
        user.password = make_password(form.clean_password())
        user.fail_login_count = 0
        user.save()

        ur.is_deleted = True
        ur.is_success = True
        ur.save()

        return JsonResponse(f.get_json_success_message(['パスワードをリセットしました','続けてログインしてください']))
    
    def get_user_reset(self):
        return f.get_object_or_404_from_q(UserReset.objects.active(one_time_id=f.get_dict_item(self.kwargs, 'one_time_id')))

class SendMailForResetPasswordView(SendMailView, ResetPasswordBaseView):
    form_class = SendMailForm
    template_name = 'pages/send_mail_for_reset_password.html'
    mail_title = 'パスワードリセット'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        username = f.get_dict_item(request.POST, 'username')
        email = form.clean_email()
        
        user = f.get_from_queryset(User.objects.active(username=username ,email=email))
        #todo (低) メールを送信しない場合とする場合のレスポンス時間を同一にする
        if user is None:
            return self.get_success_json_response()

        ur = UserReset.objects.get_or_none(user=user)
        if ur is None:
            ur = UserReset.objects.create(user=user, one_time_id=self.get_one_time_id())
            self.send_mail(self.mail_title, self.get_reset_message(ur.one_time_id), [user.email])
            return self.get_success_json_response()

        if f.get_diff_seconds_from_now(ur.updated_at) < self.resettable_seconds:
            return JsonResponse(f.get_json_error_message(['間隔を空けてください']))

        #todo (低) メールを送信するなら回数制限，モーダルエラーなら登録しているメールアドレスがバレないように．．．
        if f.get_diff_seconds_from_now(user.updated_at) < self.resettable_interval:
            next_reset = make_naive(user.updated_at) + timedelta(seconds=self.resettable_interval)
            message = '前回パスワードリセットした時刻と間隔が短すぎます．\
                \n次回パスワードリセットできるのは{}以降です．'.format(next_reset.strftime('%Y年%m月%d日 %H:%M'))
            self.send_mail(self.mail_title, message, [user.email])
            return self.get_success_json_response()
        
        ur.update(one_time_id = self.get_one_time_id(), is_deleted=False)
        self.send_mail(self.mail_title, self.get_reset_message(ur.one_time_id), [user.email])

        return self.get_success_json_response()

    def get_reset_message(self, one_time_id):
        return '以下のURLからパスワードをリセットしてください\
            \n{}/reset-password/{}/\
            \n（期限：5分以内）'.format(self.get_base_path(), one_time_id)

class GetUserView(UserItemView, ListView):
    model = settings.AUTH_USER_MODEL
    
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        target_user = f.get_object_or_404_from_q(User.objects.active(username=f.get_dict_item(self.kwargs, 'username')))
        return JsonResponse(self.get_user_item(target_user.profile))

class UserProfileView(LoginRequiredMixin, HeaderView, UserItemView, TemplateView):
    form_class = UserProfileForm
    template_name = 'pages/profile.html'
    model = settings.AUTH_USER_MODEL
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def post(self, request, *args, **kwargs):
        form_data = request.POST
        form = self.form_class(form_data)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        files = request.FILES
        profile = request.user.profile
        img_list = f.get_img_list(form_data, files, self.max_img, [profile.img])

        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        if not f.is_empty(img_list[0]):
            profile.img = img_list[0]

        profile.profession = form.clean_profession()
        profile.description = form.clean_description()

        tags_str = f.get_dict_item(request.POST, 'tags')
        if not f.is_empty(tags_str):
            tags = tags_str.split(',')
            if profile.tag_sequence is None:
                profile.tag_sequence = TagSequence.objects.create()
            profile.tag_sequence.tag1 = f.get_tag(f.get_list_item(tags, 0), self.request.user)
            profile.tag_sequence.tag2 = f.get_tag(f.get_list_item(tags, 1), self.request.user)
            profile.tag_sequence.tag3 = f.get_tag(f.get_list_item(tags, 2), self.request.user)
            profile.tag_sequence.tag4 = f.get_tag(f.get_list_item(tags, 3), self.request.user)
            profile.tag_sequence.tag5 = f.get_tag(f.get_list_item(tags, 4), self.request.user)
            profile.tag_sequence.save()

        profile.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['img_path'] = f.get_img_path(profile.img)
        context['profession'] = profile.profession
        context['description'] = profile.description
        context['user_tags'] = self.get_profile_tags(profile)

        context['room_guests'] = self.get_accept_room_guests()
        context['invited_rooms'] = self.get_invited_rooms()

        return context

    def get_accept_room_guests(self):
        data = []
        rooms = Room.objects.active(admin=self.request.user)
        for room in rooms:
            room_guests = list(RoomGuest.objects.active(room=room).values_list('guest__username', flat=True))
            if len(room_guests) == 0:
                continue
            data.append({
                'room_id':room.id,
                'room_title':room.title,
                'guests':room_guests
            })

        return data

    def get_invited_rooms(self):
        data = []
        invite_rooms = RoomInviteUser.objects.active(user=self.request.user)
        for invite_room in invite_rooms:
            data.append({
                'room_id':invite_room.room.id,
                'room_title':invite_room.room.title,
                'admin':invite_room.room.admin,
            })

        return data
