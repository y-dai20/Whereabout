from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.views.generic import CreateView, TemplateView, ListView, View
from django.conf import settings
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.utils.timezone import make_naive
from django.contrib import messages
from django.shortcuts import render


from base.views.exceptions import MyBadRequest
from base.forms import SignUpForm, ChangePasswordForm, SendMailForm, UserProfileForm
from base.models import Room, RoomGuest, Profile
from base.models.room_models import RoomInviteUser, RoomUser, RoomAuthority
from base.models.account_models import User, Guest, UserReset
from base.views.functions import \
    get_diff_seconds_from_now, create_id, get_dict_item, get_img_path, is_empty,\
    get_json_success_message, get_json_error_message, get_file_size_by_unit, get_form_error_message,\
    get_img_list, get_file_size
from base.views.general_views import UserItemView, SendMailView, HeaderView
from base.views.mixins import LoginRequiredMixin

from datetime import datetime, timedelta

class LoginView(LoginView):
    template_name = 'pages/login.html'
    max_fail_login_count = 5
    
    #todo (低) login with username, email, password
    def post(self, request, *args, **kwargs):
        user = self.get_user()
        if user.exists() and user[0].fail_login_count > self.max_fail_login_count:
            messages.error(self.request, 'ログイン失敗回数が許容範囲を超えました')
            messages.error(self.request, 'パスワードリセットを試してください')
            return render(self.request, self.template_name)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_user()
        user = user[0]
        user.fail_login_count = 0
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ユーザー名かパスワードが間違っています')
        
        user = self.get_user()
        if user.exists():
            user = user[0]
            user.fail_login_count = user.fail_login_count + 1
            user.save()
        return super().form_invalid(form)
    
    def get_user(self):
        return User.objects.filter(username=get_dict_item(self.request.POST, 'username'), is_active=True)

class SignUpView(CreateView):
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
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        # emailが過去に使用されていれば，使用禁止にする
        user = User.objects.filter(email=self.guest.email)
        if user.exists():
            raise MyBadRequest

        if get_diff_seconds_from_now(self.guest.updated_at) > self.registrable_seconds:
            return JsonResponse(get_json_error_message(['時間切れです', 'メールアドレスの登録からやり直してください']))

        user = form.save()
        self.guest.is_deleted = True
        self.guest.save()
        
        # adminのRoomに強制参加
        rooms = Room.objects.filter(title="admin", admin__username="admin")
        if rooms.exists():
            RoomUser.objects.create(
                room=rooms[0],
                user=user,
                authority=RoomAuthority.objects.create(
                    can_reply=rooms[0].authority.can_reply, 
                    can_post=rooms[0].authority.can_post, 
                    is_admin=rooms[0].authority.is_admin
                ),
            )

        login(request, user)
        return JsonResponse(get_json_success_message(['ユーザー登録しました']))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.guest.email
        return context

    def get_guest(self):
        return get_object_or_404(Guest, one_time_id=get_dict_item(self.kwargs, 'one_time_id'), is_deleted=False)

class SendMailForSignupView(SendMailView):
    form_class = SendMailForm
    template_name = 'pages/send_mail_for_signup.html'
    max_access_count = 3
    send_mail_interval = 24 * 60 * 60

    #todo (低) 嫌がらせ対策が必要
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        self.email = form.clean_email()        
        guest = Guest.objects.filter(email=self.email)
        if guest.exists():
            if get_diff_seconds_from_now(guest[0].updated_at) > self.send_mail_interval:
                guest[0].access_count = 0

            if guest[0].access_count > self.max_access_count:
                return JsonResponse(get_json_error_message([
                    '入力したメールアドレスに対してのアクセス回数が許容範囲を超えています', 
                    '登録するメールアドレスを変更するか，1日以上の間隔を空けて再度登録してください']))

            message = self.get_register_message(guest[0].one_time_id)
            access_count = guest[0].access_count
            guest.update(access_count=access_count+1, one_time_id=create_id(self.one_time_id_len), is_deleted=False)
            guest = guest[0]
        else:
            guest = Guest.objects.create(email=self.email, one_time_id=create_id(self.one_time_id_len))
            message = self.get_register_message(guest.one_time_id)
        
        user = User.objects.filter(email=self.email)
        if user.exists():
            message = 'このメールアドレスで既にユーザー登録されています'

        self.send_mail(
            'YourRoom：ユーザ登録',
            message,
            [self.email], 
        )
        return JsonResponse(get_json_success_message(['【{}】から【{}】宛にメールを送信しました'.format(self.user_from, self.email)]))

    def get_register_message(self, id):
        return '\
        以下のURLをクリックしてユーザー登録を完了してください．\
        \n{}/signup/{}/\
        \n(期限：5分以内)'.format(settings.MY_URL, id)

#todo (低) 変更の回数制限は不要？
class ChangePasswordView(LoginRequiredMixin, View):
    form_class = ChangePasswordForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(get_json_error_message(get_form_error_message(form)))
        
        user = request.user
        user.password = make_password(form.clean_password())
        user.fail_login_count = 0
        user.save()

        login(request, user)

        return JsonResponse(get_json_success_message(['パスワードを変更しました']))

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
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        if get_diff_seconds_from_now(ur.updated_at) > self.resettable_seconds:
            return JsonResponse(get_json_error_message(['時間切れです', 'もう一度メール送信からやり直してください']))

        user = ur.user
        ur.prev_password = user.password
        user.password = make_password(form.clean_password())
        user.fail_login_count = 0
        user.save()

        ur.is_deleted = True
        ur.is_success = True
        ur.save()

        return JsonResponse(get_json_success_message(['パスワードをリセットしました','続けてログインしてください']))
    
    def get_user_reset(self):
        return get_object_or_404(UserReset, one_time_id=get_dict_item(self.kwargs, 'one_time_id'), is_deleted=False)

class SendMailForResetPasswordView(SendMailView, ResetPasswordBaseView):
    form_class = SendMailForm
    template_name = 'pages/send_mail_for_reset_password.html'
    mail_title = 'パスワードリセット'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        username = get_dict_item(request.POST, 'username')
        email = form.clean_email()
        
        user = User.objects.get_or_none(username=username ,email=email, is_active=True)
        #todo (低) メールを送信しない場合とする場合のレスポンス時間を同一にする
        if user is None:
            return self.get_success_json_response()

        ur = UserReset.objects.get_or_none(user=user)
        if ur is None:
            ur = UserReset.objects.create(user=user, one_time_id=create_id(self.one_time_id_len))
            self.send_mail(self.mail_title, self.get_reset_message(ur.one_time_id), [user.email])
            return self.get_success_json_response()

        if get_diff_seconds_from_now(ur.updated_at) < self.resettable_seconds:
            return JsonResponse(get_json_error_message(['間隔を空けてください']))

        #todo (低) メールを送信するなら回数制限，モーダルエラーなら登録しているメールアドレスがバレないように．．．
        if get_diff_seconds_from_now(user.updated_at) < self.resettable_interval:
            next_reset = make_naive(user.updated_at) + timedelta(seconds=self.resettable_interval)
            message = '前回パスワードリセットした時刻と間隔が短すぎます．\
                \n次回パスワードリセットできるのは{}以降です．'.format(next_reset.strftime('%Y年%m月%d日 %H:%M'))
            self.send_mail(self.mail_title, message, [user.email])
            return self.get_success_json_response()
        
        ur.update(one_time_id = create_id(self.one_time_id_len), is_deleted=False)
        self.send_mail(self.mail_title, self.get_reset_message(ur.one_time_id), [user.email])

        return self.get_success_json_response()

    def get_reset_message(self, one_time_id):
        return '以下のURLからパスワードをリセットしてください\
            \n{}/reset-password/{}/\
            \n（期限：5分以内）'.format(settings.MY_URL, one_time_id)

class GetUserView(UserItemView, ListView):
    model = settings.AUTH_USER_MODEL
    
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=get_dict_item(self.kwargs, 'username'), is_active=True)
        return JsonResponse(self.get_user_item(target_user.profile))

class UserProfileView(LoginRequiredMixin, HeaderView, TemplateView):
    form_class = UserProfileForm
    template_name = 'pages/profile.html'
    model = settings.AUTH_USER_MODEL
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def post(self, request, *args, **kwargs):
        form_data = request.POST
        form = self.form_class(form_data)
        if not form.is_valid():
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        files = request.FILES
        img_list = get_img_list(form_data, files, self.max_img)
        if get_file_size(img_list) > self.max_img_size:
            return JsonResponse(get_json_error_message(['画像サイズが{}を超えています'.format(get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        profile = request.user.profile
        profile.img = img_list[0]

        profile.profession = form.clean_profession()
        profile.description = form.clean_description()
        profile.save()

        return JsonResponse(get_json_success_message(['保存しました']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['img_path'] = get_img_path(profile.img)
        context['profession'] = profile.profession
        context['description'] = profile.description

        context['room_guests'] = self.get_accept_room_guests()
        context['invited_rooms'] = self.get_invited_rooms()

        return context

    def get_accept_room_guests(self):
        data = []
        rooms = Room.objects.filter(admin=self.request.user, is_deleted=False)
        for room in rooms:
            room_guests = list(RoomGuest.objects.filter(room=room, is_deleted=False).values_list('guest__username', flat=True))
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
        invite_rooms = RoomInviteUser.objects.filter(user=self.request.user, is_deleted=False)
        for invite_room in invite_rooms:
            data.append({
                'room_id':invite_room.room.id,
                'room_title':invite_room.room.title,
                'admin':invite_room.room.admin,
            })

        return data
