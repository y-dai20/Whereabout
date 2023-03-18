from django.views.generic import ListView, CreateView, UpdateView, TemplateView, View
from django.http import JsonResponse, Http404
from django.db.models.functions import Length
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.shortcuts import redirect

import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.models.general_models import Personal, TagSequence
from base.models.account_models import User, UserBlock
from base.models.post_models import Post, PostFavorite
from base.models.room_models import Room, RoomGuest, RoomUser, RoomGood, RoomAuthority, RoomTab, \
    RoomTabItem, RoomInviteUser, RoomReplyType, RoomTabSequence, RoomRequestInformation, RoomInformation
from base.views.general_views import ShowRoomBaseView, PostItemView, RoomItemView, RoomBase, SearchBaseView, GoodView
from base.views.validate_views import ValidateRoomView
from base.forms import CreateRoomForm, UpdateRoomForm, RoomRequestInformationForm, PersonalForm
from base.views.mixins import LoginRequiredMixin, RoomAdminRequiredMixin, RoomAccessRequiredMixin

import json

class ShowRoomView(ShowRoomBaseView, SearchBaseView, PostItemView):
    template_name = 'pages/room.html'
    model = Room
    load_by = 20
    max_star = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'',
            'title':'',
            'date_from':'',
            'date_to':'',
            'is_favorite':'',
            'tags':'',
        }

    def get_items(self):
        params = self.get_params()
        posts = Post.objects.active(
            user__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            room=self.room,
        )
        if params['is_favorite'] and self.request.user.is_authenticated:
            fav_ids = PostFavorite.objects.active(user=self.request.user, obj__room=self.room).values_list('obj__id', flat=True)
            posts = posts.filter(id__in=fav_ids)
        
        if not f.is_empty(params['tags']):
            posts = posts.annotate(
                tags=Concat(V('&'), 'tag_sequence__tag1__name', 
                            V('&'), 'tag_sequence__tag2__name', 
                            V('&'), 'tag_sequence__tag3__name', 
                            V('&'), 'tag_sequence__tag4__name',
                            V('&'), 'tag_sequence__tag5__name', V('&')))
            for tag in params['tags'].split(','):
                posts = posts.filter(tags__contains='&{}&'.format(tag))


        return self.get_post_items(self.get_idx_items(posts))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['star_denominator'] = self.room.good_count + self.room.bad_count
        context['max_star'] = self.max_star
        context['star_rate'] = round(self.room.good_count / context['star_denominator'], 1) * self.max_star if context['star_denominator'] > 0 else 0.0

        return context

#todo (高) ルームの情報をどこかに表示する
class ShowRoomTabView(ShowRoomView):
    template_name = 'pages/room_tab.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        room_tab = f.get_object_or_404_from_q(RoomTab.objects.active(id=f.get_dict_item(self.kwargs, 'room_tab_pk'), room=self.room))
        context['target_tab_title'] = room_tab.title
        context['target_tab_id'] = room_tab.id
        context['target_tab_items'] = self.room_base.get_room_tab_items(room_tab)

        for idx, room_tab in enumerate(context['room_tabs']):
            if room_tab['id'] == context['target_tab_id']:
                context['target_tab_sequence'] = idx
                break

        return context

class ManageRoomBaseView(LoginRequiredMixin, RoomAdminRequiredMixin, View):
    max_img = 5
    
    def __init__(self):
        super().__init__()
        self.vr = None
        self.error_messages = []

    def get_validate_room(self):
        vr = ValidateRoomView(f.get_dict_item(self.kwargs, 'room_pk'))
        if not vr.is_room_exist():
            raise MyBadRequest('room is not exist.')
        return vr

class GetRoomTabItems(TemplateView):
    def post(self, request, *args, **kwargs):
        room_tab_id = f.get_dict_item(request.POST, 'room_tab_id')
        if f.is_empty(room_tab_id) or not f.is_str(room_tab_id):
            raise MyBadRequest('room_tab_id is error.')
        
        room_tab = RoomTab.objects.get_object_or_404(id=room_tab_id)
        vr = ValidateRoomView(room_tab.room)
        if not vr.check_access(request.user):
            raise MyBadRequest('room access error.')

        room_base = RoomBase()
        return JsonResponse(f.get_json_success_message(add_dict={
            'room_tab_items':room_base.get_room_tab_items(room_tab_id),
        }))

#todo (低) ルームに電話番号，住所など情報追加
class ManageRoomView(ManageRoomBaseView, ShowRoomBaseView, ListView):
    model = RoomUser
    template_name = 'pages/manage_room.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if f.is_empty(self.vr):
            self.vr = self.get_validate_room()
        
        room = self.vr.get_room()
        room_users = RoomUser.objects.active(room=room, is_blocked=False)
        room_invite_users = RoomInviteUser.objects.active(room=room)
        room_blocked_users = RoomUser.objects.active(room=room, is_blocked=True)
        room_guests = RoomGuest.objects.active(room=room)

        room_base = RoomBase(room)
        context['defo_authority'] = room.authority
        context['room_users'] = room_users
        context['room_blocked_users'] = room_blocked_users
        context['room_invite_users'] = room_invite_users
        context['room_guests'] = room_guests
        context['reply_types'] = room_base.get_room_reply_types(is_unique=False)
        img_sizes = room_base.get_room_img_size()
        context['img_path_and_size'] = f.get_combined_list('path', f.get_dict_item_list(context, 'img_paths'),'size',img_sizes)
        context['total_img_size'] = {'b':sum(img_sizes), 'mb':f.get_file_size_by_unit(sum(img_sizes), 'MB')}
        context['video_size'] = room.video.file.size if bool(room.video) else 0
        request_information = room_base.get_room_request_information()
        context['request_information'] = request_information
        
        room_information_list = []
        for room_user in room_users:
            information = []
            for rri in request_information:
                if f.is_empty(rri):
                    information.append('')
                    continue
                ri = f.get_from_queryset(RoomInformation.objects.active(rri=rri['id'], user=room_user.user))
                if ri is None:
                    information.append('')
                else:
                    information.append(ri.text)
            room_information_list.append({
                'username':room_user.user.username,
                'information':information
            })

        context['room_information_list'] = room_information_list

        return context

class CreateRoomView(LoginRequiredMixin, CreateView):
    form_class = CreateRoomForm
    model = Room
    max_room_count = 1
    max_img = 5
    max_img_size = 2 * 1024 * 1024

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        room = form.save(commit=False)
        if Room.objects.active(title=room.title, admin=request.user).exists():
            return JsonResponse(f.get_json_error_message(['同じタイトルのルームは作成できません']))

        if Room.objects.active(admin=request.user).count() >= self.max_room_count and not request.user.is_admin:
            return JsonResponse(f.get_json_error_message(['{}個以上のRoomは作成できません'.format(self.max_room_count)]))

        room.admin = request.user
        room.authority = RoomAuthority.objects.create(can_reply=True)

        files = request.FILES
        img_list = f.get_img_list(request.POST, files, self.max_img)
        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        
        room.img1 = img_list[0]
        room.img2 = img_list[1]
        room.img3 = img_list[2]
        room.img4 = img_list[3]
        room.img5 = img_list[4]

        room.save()

        return JsonResponse(f.get_json_success_message(['ルームを作成しました'], {'room_id':room.id, 'room_title':room.title}))

class DeleteRoomView(ManageRoomBaseView, TemplateView):
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        room = vr.get_room()
        room.is_deleted = True
        room.save()

        return JsonResponse(f.get_json_success_message(['削除しました'], {'href':'/rooms/'}))

#todo (中) request informationがあれば表示するようにする
class JoinRoomView(LoginRequiredMixin, CreateView):
    model = RoomGuest

    def get(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_room_exist() or not vr.is_public() or vr.is_admin(request.user):
            raise MyBadRequest('room is not exist.')
        
        room = vr.get_room()
        if UserBlock.objects.active(blocker=room.admin, blockee=request.user).exists():
            return JsonResponse(f.get_json_error_message(['管理者にブロックされています']))

        room_user = RoomUser.objects.get_or_none(user=request.user, room=room)
        if room_user is not None and not room_user.is_deleted:
            return JsonResponse(f.get_json_error_message(['すでに参加しています']))

        room_guest = RoomGuest.objects.get_or_none(guest=request.user, room=room)
        if room_guest is not None and not room_guest.is_deleted:
            return JsonResponse(f.get_json_error_message(['参加申請中です']))
        
        if room.need_approval:
            if room_guest is not None:
                room_guest.is_deleted = False
                room_guest.save()
            else:
                room_guest.create(guest=request.user, room=room)
            return JsonResponse(f.get_json_success_message(['参加申請を出しました'], {'is_waiting':True}))

        if room_user is not None:
            room_user.is_deleted = False
            room_user.is_blocked = False
            room_user.save()
        else:
            RoomUser.objects.create(
                room=room, 
                user=request.user, 
                authority=RoomAuthority.objects.create(
                    can_reply=room.authority.can_reply, 
                    can_post=room.authority.can_post, 
                    is_admin=room.authority.is_admin
                ),
            )
        room.participant_count += 1
        room.save()

        return JsonResponse(f.get_json_success_message(['参加しました'], {'is_waiting':False}))

class LeaveRoomView(LoginRequiredMixin, UpdateView):
    model = RoomUser

    def get(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_room_exist() or vr.is_admin(request.user):
            raise MyBadRequest('room is not exist.')
        
        room_user = vr.get_room_user(request.user)
        if not room_user.exists():
            raise MyBadRequest('RoomUser is not exist.')

        room_user.is_deleted = True
        room_user.save()

        room = vr.get_room()
        room.participant_count -= 1
        room.save()

        return redirect('/rooms/')

class AcceptRoomInviteView(LoginRequiredMixin, CreateView):
    model = RoomInviteUser

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_room_exist():
            raise MyBadRequest('room is not exist.')
        room = vr.get_room()
        room_invite = f.get_object_or_404_from_q(RoomInviteUser.objects.active(room=room, user=request.user))

        is_accept = f.get_boolean_or_none(f.get_dict_item(request.POST, 'is_accept'))
        if is_accept is None:
            raise MyBadRequest('is_accept is None.')
        
        room_user = RoomUser.objects.get_or_none(room=room, user=request.user)
        if room_user is not None and not room_user.is_deleted:
            return JsonResponse(f.get_json_error_message(['エラーが発生しました．(E03)']))

        if is_accept:
            if room_user is None:
                RoomUser.objects.create(
                    room=room, 
                    user=request.user, 
                    authority=RoomAuthority.objects.create(
                        can_reply=room.authority.can_reply, 
                        can_post=room.authority.can_post, 
                        is_admin=room.authority.is_admin
                    ),
                )
            else:
                room_user.is_deleted = False
                room_user.save()
            room.participant_count += 1
            room.save()

        room_invite.is_deleted = True
        room_invite.save()

        return JsonResponse(f.get_json_success_message())

class AcceptRoomGuestView(ManageRoomBaseView, CreateView):
    model = RoomInviteUser
    
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        is_blocked = f.get_boolean_or_none(f.get_dict_item(request.POST, 'is_blocked'))
        if is_blocked is None:
            raise MyBadRequest('is_blocked is None.')

        result = self.accept_room_guest(f.get_dict_item(kwargs, 'username'), f.get_dict_item(kwargs, 'room_pk'), is_blocked)
        if not result:
            return JsonResponse(f.get_json_error_message(['エラーが発生しました．(E02)']))

        return JsonResponse(f.get_json_success_message())

    def accept_room_guest(self, username, room, is_blocked=False):
        guest = f.get_object_or_404_from_q(User.objects.active(username=username))
        vr = ValidateRoomView(room)
        if not vr.is_room_exist() or not vr.is_admin(self.request.user):
            return False
        
        room = vr.get_room()
        room_guest = f.get_object_or_404_from_q(RoomGuest.objects.active(room=room, guest=guest))
        
        room_user = RoomUser.objects.get_or_none(room=room, user=guest)
        if room_user is not None and not room_user.is_deleted:
            return False

        if room_user is None:
            RoomUser.objects.create(
                room=room, 
                user=guest,
                is_blocked=is_blocked, 
                authority=RoomAuthority.objects.create(
                    can_reply=room.authority.can_reply, 
                    can_post=room.authority.can_post, 
                    is_admin=room.authority.is_admin
                ),
            )
        else:
            room_user.is_deleted = False
            room_user.save()

        if not is_blocked: 
            room.participant_count += 1
            room.save()

        room_guest.is_deleted = True
        room_guest.save()
        return True

#todo (低) modal search base viewを作ろう
class ModalSearchRoomView(ListView):
    model = Room
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        word = f.get_dict_item(request.GET, 'search_word')
        if not f.is_str(word):
            raise MyBadRequest('search_word is not str.')
        rooms = Room.objects.active(title__icontains=word).public()\
                .exclude(id__in=RoomBase.get_my_room_list(request.user))\
                    .order_by('-title')\
                        .order_by(Length('title').desc())

        return JsonResponse(f.get_json_success_message(add_dict={
            'rooms':[{'id':room.id, 'title':room.title, 'admin':room.admin.username, 'user_img':f.get_img_path(room.admin.profile.img)} for room in rooms]}))

class ModalSearchUserView(ListView):
    model = User
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        word = f.get_dict_item(request.GET, 'search_word')
        if not f.is_str(word):
            raise MyBadRequest('search_word is not str.')

        users = User.objects.active(username__icontains=word)
        if request.user.is_authenticated:
            users = users.exclude(id=request.user.id)
        users = users.order_by('-username').order_by(Length('username').desc())

        return JsonResponse(f.get_json_success_message(add_dict={
            'users':[{'user_img':f.get_img_path(user.profile.img), 'user_id':user.id, 'username':user.username} for user in users]}))

class ManageRoomAuthorityView(ManageRoomBaseView, TemplateView):
    model = RoomUser
    template_name = 'pages/manage_room.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        room = vr.get_room()
        json_data = json.loads(request.body.decode('utf-8'))

        for jd in f.get_dict_item_list(json_data, 'checks'):
            ru = f.get_object_or_404_from_q(RoomUser.objects.active(room=room, user__username=f.get_dict_item(jd, 'username')))
            auth = f.get_from_queryset(RoomAuthority.objects.active(id=ru.authority.id))
            can_reply, can_post, is_admin = self.get_authority_check(jd)
            if can_reply is not None:
                auth.can_reply = can_reply
            if can_post is not None:
                auth.can_post = can_post
            if is_admin is not None:
                auth.is_admin = is_admin
            auth.save()

        default = f.get_dict_item_list(json_data, 'defa')
        if not f.is_empty(default):
            auth = f.get_from_queryset(RoomAuthority.objects.active(id=room.authority.id))
            can_reply, can_post, is_admin = self.get_authority_check(default)
            if can_reply is not None:
                auth.can_reply = can_reply
            if can_post is not None:
                auth.can_post = can_post
            if is_admin is not None:
                auth.is_admin = is_admin
            auth.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))
    
    def get_authority_check(self, data):
        can_reply = f.get_boolean_or_none(f.get_dict_item(data, 'can_reply'))
        can_post = f.get_boolean_or_none(f.get_dict_item(data, 'can_post'))
        is_admin = f.get_boolean_or_none(f.get_dict_item(data, 'is_admin'))

        return can_reply, can_post, is_admin

class ManageRoomParticipantView(AcceptRoomGuestView, TemplateView):
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body.decode('utf-8'))
        vr = self.get_validate_room()
        self.room = vr.get_room()
        need_approval = f.get_boolean_or_none(f.get_dict_item(json_data, 'need_approval'))
        if need_approval is not None:
            self.room.need_approval = need_approval

        for username in f.get_dict_item_list(json_data, 'accept_users'):
            self.accept_room_guest(username, self.room, False)
        for username in f.get_dict_item_list(json_data, 'disaccept_users'):
            self.accept_room_guest(username, self.room, True)
        for username in f.get_dict_item_list(json_data, 'banish_users'):
            self.toggle_banish_user(username)
        for username in f.get_dict_item_list(json_data, 'cancel_invite_users'):
            self.cancel_invite_user(username)
        
        self.room.participant_count = RoomUser.objects.active(room=self.room).count()
        self.room.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

    def toggle_banish_user(self, username):
        if f.is_empty(username):
            return False
        room_user = f.get_object_or_404_from_q(RoomUser.objects.active(room=self.room, user__username=username))
        room_user.is_blocked = not room_user.is_blocked
        room_user.save()
        return True

    def cancel_invite_user(self, username):
        if f.is_empty(username):
            return False
        invite_obj = f.get_object_or_404_from_q(RoomInviteUser.objects.active(room=self.room, user__username=username))
        invite_obj.is_deleted = True
        invite_obj.save()
        return True

#todo (中) Tabの順番をドラッグで移動できるようにする
#todo (中) 文字色や背景を変えられるようにしたい
#todo (中) タイトル内を開け閉めできるようにする
class ManageRoomDisplayView(ManageRoomBaseView, TemplateView):
    model = Room
    form_class = UpdateRoomForm
    template_name = 'pages/manage_room.html'
    max_img_size = 2 * 1024 * 1024
    max_video_size = 11 * 1024 * 1024
    max_video = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        self.room = vr.get_room()
        form_data = request.POST
        self.files = request.FILES

        form = self.form_class(form_data)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        is_public = f.get_boolean_or_none(f.get_dict_item(form_data, 'is_public'))
        if is_public is None:
            raise MyBadRequest('is_public is None.')

        self.room.is_public = is_public
        self.room.title = form.clean_title()
        self.room.subtitle = form.clean_subtitle()

        tags_str = f.get_dict_item(request.POST, 'tags')
        if not f.is_empty(tags_str):
            tags = tags_str.split(',')
            if self.room.tag_sequence is None:
                self.room.tag_sequence = TagSequence.objects.create()
            self.room.tag_sequence.tag1 = f.get_tag(f.get_list_item(tags, 0), self.request.user)
            self.room.tag_sequence.tag2 = f.get_tag(f.get_list_item(tags, 1), self.request.user)
            self.room.tag_sequence.tag3 = f.get_tag(f.get_list_item(tags, 2), self.request.user)
            self.room.tag_sequence.tag4 = f.get_tag(f.get_list_item(tags, 3), self.request.user)
            self.room.tag_sequence.tag5 = f.get_tag(f.get_list_item(tags, 4), self.request.user)
            self.room.tag_sequence.tag6 = f.get_tag(f.get_list_item(tags, 5), self.request.user)
            self.room.tag_sequence.tag7 = f.get_tag(f.get_list_item(tags, 6), self.request.user)
            self.room.tag_sequence.tag8 = f.get_tag(f.get_list_item(tags, 7), self.request.user)
            self.room.tag_sequence.tag9 = f.get_tag(f.get_list_item(tags, 8), self.request.user)
            self.room.tag_sequence.tag10 = f.get_tag(f.get_list_item(tags, 9), self.request.user)
            self.room.tag_sequence.save()

        video_list = f.get_video_list(form_data, self.files, self.max_video, [self.room.video])
        if f.get_file_size(video_list) > self.max_video_size:
            return JsonResponse(f.get_json_error_message(['動画サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_video_size, unit='MB'))]))
        self.room.video = video_list[0]
        self.room.save()

        img_list = f.get_img_list(form_data, self.files, self.max_img, [self.room.img1, self.room.img2, self.room.img3, self.room.img4, self.room.img5])

        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))

        self.room.img1 = img_list[0]
        self.room.img2 = img_list[1]  
        self.room.img3 = img_list[2]  
        self.room.img4 = img_list[3]  
        self.room.img5 = img_list[4]  
        self.room.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

class ManageRoomTabView(ManageRoomBaseView, TemplateView):
    model = Room
    template_name = 'pages/manage_room.html'
    max_tab_title_len = 32
    max_img_size = 2 * 1024 * 1024
    max_tab_title_item_len = 255
    max_tab_title_text_len = 1024

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        self.room = vr.get_room()
        form_data = request.POST
        self.files = request.FILES

        tabs = f.literal_eval(f.get_dict_item(form_data, 'tabs'))
        room_tab_sequence = f.get_object_or_404_from_q(RoomTabSequence.objects.active(room=self.room))
        room_tab_sequence.tab1 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 0), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 0), 'title'))
        room_tab_sequence.tab2 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 1), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 1), 'title'))
        room_tab_sequence.tab3 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 2), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 2), 'title'))
        room_tab_sequence.tab4 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 3), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 3), 'title'))
        room_tab_sequence.tab5 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 4), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 4), 'title'))
        room_tab_sequence.tab6 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 5), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 5), 'title'))
        room_tab_sequence.tab7 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 6), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 6), 'title'))
        room_tab_sequence.tab8 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 7), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 7), 'title'))
        room_tab_sequence.tab9 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 8), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 8), 'title'))
        room_tab_sequence.tab10 = self.get_room_tab(f.get_dict_item(f.get_list_item(tabs, 9), 'room_tab_id'), f.get_dict_item(f.get_list_item(tabs, 9), 'title'))

        self.set_room_tab_items(room_tab_sequence.tab1, f.get_dict_item(f.get_list_item(tabs, 0), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab2, f.get_dict_item(f.get_list_item(tabs, 1), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab3, f.get_dict_item(f.get_list_item(tabs, 2), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab4, f.get_dict_item(f.get_list_item(tabs, 3), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab5, f.get_dict_item(f.get_list_item(tabs, 4), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab6, f.get_dict_item(f.get_list_item(tabs, 5), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab7, f.get_dict_item(f.get_list_item(tabs, 6), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab8, f.get_dict_item(f.get_list_item(tabs, 7), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab9, f.get_dict_item(f.get_list_item(tabs, 8), 'items'))
        self.set_room_tab_items(room_tab_sequence.tab10, f.get_dict_item(f.get_list_item(tabs, 9), 'items'))

        if not f.is_empty(self.error_messages):
            return JsonResponse(f.get_json_error_message(self.error_messages))
            
        room_tab_sequence.save()
        return JsonResponse(f.get_json_success_message(['保存しました']))

    def get_room_tab(self, room_tab_id, title):
        if f.is_empty(title):
            return None
        if len(title) > self.max_tab_title_len:
            self.error_messages.append('タブのタイトルは{}文字以内に収めてください'.format(self.max_tab_title_len))
            return None
        
        room_tab = f.get_from_queryset(RoomTab.objects.active(id=room_tab_id))
        if room_tab is None:
            return RoomTab.objects.create(title=title, room=self.room)
        
        if room_tab.title == title:
            return room_tab

        if room_tab.room != self.room:
            room_tab.room = self.room
        room_tab.title = title
        room_tab.save()

        return room_tab

    def set_room_tab_items(self, room_tab, data):
        if f.is_empty(room_tab):
            return False

        self.delete_room_tab_items(room_tab, f.get_dict_item_list(data, 'delete'))
        self.create_room_tab_items(room_tab, f.get_dict_item_list(data, 'create'))

    def create_room_tab_items(self, room_tab, tab_items):
        for tab_item in tab_items:
            row = f.get_dict_item(tab_item, 'row')
            column = f.get_dict_item(tab_item, 'column')
            col = f.get_dict_item(tab_item, 'col')
            
            if not f.is_int(row) or not f.is_int(column) or not f.is_int(col):
                raise MyBadRequest('is_int error at create_room_tab_items.')

            title = f.get_dict_item(tab_item, 'title', is_strip=False)
            text = f.get_dict_item(tab_item, 'text', is_strip=False)
            img = f.get_dict_item(tab_item, 'img')

            error_place = '{}行,{}列'.format(row, column)
            if len(title) > self.max_tab_title_item_len:
                self.error_messages.append('{} タイトルの長さが{}を超えています'.format(error_place, self.max_tab_title_item_len))
                continue
            if len(text) > self.max_tab_title_text_len:
                self.error_messages.append('{} テキストの長さが{}を超えています'.format(error_place, self.max_tab_title_text_len))
                continue

            if img in self.files and f.is_uploaded_file_img(self.files[img]):
                img = self.files[img]
                if not f.is_empty(img) and f.get_file_size([img]) > self.max_img_size:
                    self.error_messages.append('{} 画像サイズが{}を超えています'.format(
                        error_place, f.get_file_size_by_unit(self.max_video_size, unit='MB')))
                    continue

            if not f.is_same_empty_count([title, text, img], 2):
                raise MyBadRequest('is_same_empty error at create_room_tab_items.')

            items = RoomTabItem.objects.active(
                row=row, 
                column=column, 
                room_tab=room_tab,
            )

            if items.exists():
                items.update(title=title, text=text, img=img, col=col)
                continue

            RoomTabItem.objects.create(
                title=title, 
                text=text, 
                img=img, 
                row=row, 
                column=column, 
                col=col,
                room_tab=room_tab
            )

        return True

    def delete_room_tab_items(self, room_tab, tab_items):
        for tab_item in tab_items:
            row = f.get_dict_item(tab_item, 'row')
            column = f.get_dict_item(tab_item, 'column')
            col = f.get_dict_item(tab_item, 'col')

            if not f.is_int(row) or not f.is_int(column) or not f.is_int(col):
                raise MyBadRequest('is_int error at create_room_tab_items.')

            items = RoomTabItem.objects.active(
                row=row, 
                column=column,
                col=col, 
                room_tab=room_tab,
            )

            if items.exists():
                items.update(is_deleted=True)

        return True

class ManageRoomPostView(ManageRoomBaseView, TemplateView):
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        room = vr.get_room()
        form_data = request.POST

        reply_type = f.get_object_or_404_from_q(RoomReplyType.objects.active(room=room))
        reply_type.type1 = f.get_dict_item(form_data, 'type1')
        reply_type.type2 = f.get_dict_item(form_data, 'type2')
        reply_type.type3 = f.get_dict_item(form_data, 'type3')
        reply_type.type4 = f.get_dict_item(form_data, 'type4')
        reply_type.type5 = f.get_dict_item(form_data, 'type5')
        reply_type.type6 = f.get_dict_item(form_data, 'type6')
        reply_type.type7 = f.get_dict_item(form_data, 'type7')
        reply_type.type8 = f.get_dict_item(form_data, 'type8')
        reply_type.type9 = f.get_dict_item(form_data, 'type9')
        reply_type.type10 = f.get_dict_item(form_data, 'type10')

        reply_type.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

class ManageRoomRequestInformationView(ManageRoomBaseView, TemplateView):
    form_class = RoomRequestInformationForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        room = vr.get_room()
        form_data = request.POST
        form = self.form_class(form_data)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))
        is_active = f.get_boolean_or_none(f.get_dict_item(form_data, 'is_active'))
        if is_active is None:
            raise MyBadRequest('is_active is None.')
        
        sequence = f.get_dict_item(form_data, 'sequence')
        if not f.is_int(sequence):
            raise MyBadRequest('sequence is not int.')
        
        sequence = int(sequence)
        room_base = RoomBase(room)
        if sequence < 1 or room_base.max_request_information < sequence:
            raise MyBadRequest('sequence is out of range.')
        
        rri_exist = RoomRequestInformation.objects.active(room=room, sequence=sequence)
        if rri_exist.exists():
            rri_exist.update(is_deleted=True)

        rri = form.save(commit=False)
        rri.room = vr.get_room()
        rri.is_active = is_active
        rri.sequence = sequence
        rri.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

class ManageRoomPersonalView(ManageRoomBaseView, TemplateView):
    form_class = PersonalForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = self.get_validate_room()
        room = vr.get_room()
        form_data = request.POST
        form = self.form_class(form_data)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        if room.personal is None:
            room.personal = Personal.objects.create()

        room.personal.web = form.clean_web()
        room.personal.phone = form.clean_phone()
        room.personal.zip_code = form.clean_zip_code()
        room.personal.state = form.clean_state()
        room.personal.city = form.clean_city()
        room.personal.address_1 = form.clean_address_1()
        room.personal.address_2 = form.clean_address_2()
        room.personal.mon_from = form.clean_mon_from()
        room.personal.mon_to = form.clean_mon_to()
        room.personal.tue_from = form.clean_tue_from()
        room.personal.tue_to = form.clean_tue_to()
        room.personal.wed_from = form.clean_wed_from()
        room.personal.wed_to = form.clean_wed_to()
        room.personal.thu_from = form.clean_thu_from()
        room.personal.thu_to = form.clean_thu_to()
        room.personal.fri_from = form.clean_fri_from()
        room.personal.fri_to = form.clean_fri_to()
        room.personal.sat_from = form.clean_sat_from()
        room.personal.sat_to = form.clean_sat_to()
        room.personal.sun_from = form.clean_sun_from()
        room.personal.sun_to = form.clean_sun_to()

        room.personal.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

class RoomInformationView(RoomAccessRequiredMixin, TemplateView):
    model = RoomInformation

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        rris = RoomRequestInformation.objects.active(room=vr.get_room(), is_active=True)
        form_data = request.POST
        for sequence, value in form_data.items():
            rri = rris.filter(sequence=sequence)
            if not rri.exists():
                raise MyBadRequest('RoomRequestInformation is not exist.')
            value = value.strip() if f.is_str(value) else value
            if len(value) < rri[0].min_length or rri[0].max_length < len(value):
                raise MyBadRequest("RoomInformation's value length is out of range.")
            if (type == 'num' and not f.is_int(value)) or (type == 'choice' and value not in rri[0].choice):
                raise MyBadRequest("RoomInformation's type is error.")
            
            RoomInformation.objects.create(rri=rri[0], user=request.user, text=value)

        return JsonResponse(f.get_json_success_message(['保存しました']))

class RoomInviteView(ManageRoomBaseView, TemplateView):
    model = User
    template_name = 'pages/manage_room.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body.decode('utf-8'))
        invite_user = f.get_object_or_404_from_q(User.objects.active(username=f.get_dict_item(json_data, 'username')))
        vr = self.get_validate_room()
        room = vr.get_room()
        if RoomUser.objects.active(user=invite_user, room=room).exists():
            return JsonResponse(f.get_json_error_message(['既に参加しています']))

        room_invite = RoomInviteUser.objects.get_or_none(room=room, user=invite_user)
        if room_invite is not None and not room_invite.is_deleted:
            return JsonResponse(f.get_json_error_message(['すでに招待しています']))
        
        if room_invite is not None and room_invite.is_deleted:
            return JsonResponse(f.get_json_error_message(['招待が拒否されています']))

        RoomInviteUser.objects.create(
            room=room,
            user=invite_user,
        )

        return JsonResponse(f.get_json_success_message(['招待しました']))

class RoomGoodView(RoomAccessRequiredMixin, GoodView):
    model = RoomGood
    template_name = 'pages/index_room.html'
    
    def get(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        return JsonResponse(self.get_json_data(obj=vr.get_room()))

class GetRoomView(RoomAccessRequiredMixin, RoomItemView, TemplateView):
    model = Room

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        return JsonResponse(f.get_json_success_message(add_dict=self.get_room_item(vr.get_room())))

class GetRoomRequestInformationView(RoomAccessRequiredMixin, TemplateView):
    model = RoomRequestInformation

    def get(self, request, *args, **kwargs):
        raise Http404
    
    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        room_base = RoomBase(vr.get_room())
        return JsonResponse(f.get_json_success_message(add_dict={'rri':room_base.get_room_request_information(is_active=True)}))