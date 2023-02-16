from django.views.generic import ListView, CreateView, UpdateView, TemplateView, View
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models.functions import Length


import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.models.account_models import User, UserBlock
from base.models.post_models import Post, PostFavorite
from base.models.room_models import Room, RoomGuest, RoomImgs, RoomUser, RoomGood, RoomAuthority, RoomTab, \
    RoomTabItem, RoomInviteUser, RoomReplyType, RoomTabSequence, RoomRequestInformation, RoomInformation
from base.views.general_views import ShowRoomBaseView, PostItemView, RoomItemView, RoomBase, SearchBaseView, GoodView
from base.views.validate_views import ValidateRoomView
from base.forms import CreateRoomForm, UpdateRoomForm, RoomRequestInformationForm
from base.views.mixins import LoginRequiredMixin, RoomAdminRequiredMixin

import json

class ShowRoomView(ShowRoomBaseView, SearchBaseView, PostItemView):
    template_name = 'pages/room.html'
    model = Room
    load_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'',
            'title':'',
            'date_from':'',
            'date_to':'',
            'is_favorite':'',
        }

    def get_items(self):
        params = self.get_params()
        posts = Post.objects.filter(
            is_deleted=False, 
            user__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            room=self.room,
        )
        if params['is_favorite'] and self.request.user.is_authenticated:
            fav_ids = PostFavorite.objects.filter(user=self.request.user, obj__room=self.room, is_deleted=False).values_list('obj__id', flat=True)
            posts = posts.filter(id__in=fav_ids)
        
        return self.get_post_items(self.get_idx_items(posts))

class ShowRoomTabView(ShowRoomView):
    template_name = 'pages/room_tab.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tab_title = get_object_or_404(RoomTab, id=f.get_dict_item(self.kwargs, 'tab_content_pk'), room=self.room, is_deleted=False)
        context['target_tab_title'] = tab_title.title
        context['target_tab_id'] = tab_title.id
        context['target_tab_items'] = self.room_base.get_room_tab_content_items(tab_title)

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
    
class GetRoomTabContents(TemplateView):
    def post(self, request, *args, **kwargs):
        content_id = f.get_dict_item(request.POST, 'content_id')
        if f.is_empty(content_id) or not f.is_str(content_id):
            raise MyBadRequest('content_id is error.')

        room_base = RoomBase()
        return JsonResponse(f.get_json_success_message(add_dict={'content_items':room_base.get_room_tab_content_items(content_id)}))

#todo (低) ルームに電話番号，住所など情報追加
class ManageRoomView(ManageRoomBaseView, ShowRoomBaseView, ListView):
    model = RoomUser
    template_name = 'pages/manage_room.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if f.is_empty(self.vr):
            self.vr = self.get_validate_room()
        
        room = self.vr.get_room()
        room_users = RoomUser.objects.filter(room=room, is_blocked=False, is_deleted=False)
        room_invite_users = RoomInviteUser.objects.filter(room=room, is_deleted=False)
        room_blocked_users = RoomUser.objects.filter(room=room, is_blocked=True, is_deleted=False)
        room_guests = RoomGuest.objects.filter(room=room, is_deleted=False)

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
                ri = RoomInformation.objects.get_or_none(rri=rri['id'], user=room_user.user, is_deleted=False)
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
        if Room.objects.filter(title=room.title, admin=request.user, is_deleted=False).exists():
            return JsonResponse(f.get_json_error_message(['同じタイトルのルームは作成できません']))

        if Room.objects.filter(admin=request.user, is_deleted=False).count() >= self.max_room_count and not request.user.is_admin:
            return JsonResponse(f.get_json_error_message(['{}個以上のRoomは作成できません'.format(self.max_room_count)]))

        room.admin = request.user
        room.authority = RoomAuthority.objects.create(can_reply=True)

        files = request.FILES
        img_list = f.get_img_list(request.POST, files, self.max_img)
        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))

        room.save()
        if not f.is_all_none(img_list):
            RoomImgs.objects.create(
                room=room,
                img1 = img_list[0],
                img2 = img_list[1],
                img3 = img_list[2],
                img4 = img_list[3],
                img5 = img_list[4],
            )

        return JsonResponse(f.get_json_success_message(['ルームを作成しました'], {'room_id':room.id, 'room_title':room.title}))

#todo (中) request informationがあれば表示するようにする
class JoinRoomView(LoginRequiredMixin, CreateView):
    model = RoomGuest

    def get(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_room_exist() or not vr.is_public() or vr.is_admin(request.user):
            raise MyBadRequest('room is not exist.')
        
        room = vr.get_room()
        if UserBlock.objects.filter(blocker=room.admin, blockee=request.user, is_deleted=False):
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
        
        room = vr.get_room()
        room_user = RoomUser.objects.get_or_none(user=request.user, room=room, is_blocked=False, is_deleted=False)
        if room_user is None:
            raise MyBadRequest('RoomUser is not exist.')

        room_user.is_deleted = True
        room_user.save()
        room.participant_count -= 1
        room.save()

        return redirect('/')

class AcceptRoomInviteView(LoginRequiredMixin, CreateView):
    model = RoomInviteUser

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_room_exist():
            raise MyBadRequest('room is not exist.')
        room = vr.get_room()
        room_invite = get_object_or_404(RoomInviteUser, room=room, user=request.user, is_deleted=False)

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
        guest = get_object_or_404(User, username=username, is_active=True)
        vr = ValidateRoomView(room)
        if not vr.is_room_exist() or not vr.is_admin(self.request.user):
            return False
        
        room = vr.get_room()
        room_guest = get_object_or_404(RoomGuest, room=room, guest=guest, is_deleted=False)
        
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
        rooms = Room.objects.filter(is_deleted=False, is_public=True, title__icontains=word)\
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

        users = User.objects.filter(is_active=True, username__icontains=word)
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
            ru = get_object_or_404(RoomUser, room=room, user__username=f.get_dict_item(jd, 'username'), is_deleted=False)
            auth = RoomAuthority.objects.get(is_deleted=False, id=ru.authority.id)
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
            auth = RoomAuthority.objects.get(is_deleted=False, id=room.authority.id)
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
        
        self.room.participant_count = RoomUser.objects.filter(room=self.room, is_deleted=False).count()
        self.room.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

    def toggle_banish_user(self, username):
        if f.is_empty(username):
            return False
        room_user = get_object_or_404(RoomUser, room=self.room, user__username=username, is_deleted=False)
        room_user.is_blocked = not room_user.is_blocked
        room_user.save()
        return True

    def cancel_invite_user(self, username):
        if f.is_empty(username):
            return False
        invite_obj = get_object_or_404(RoomInviteUser, room=self.room, user__username=username, is_deleted=False)
        invite_obj.is_deleted = True
        invite_obj.save()
        return True

class ManageRoomDisplayView(ManageRoomBaseView, TemplateView):
    model = Room
    form_class = UpdateRoomForm
    template_name = 'pages/manage_room.html'
    max_img_size = 2 * 1024 * 1024
    max_video_size = 11 * 1024 * 1024
    max_video = 1
    max_tab_title_len = 255
    max_tab_text_len = 255

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

        video_list = f.get_video_list(form_data, self.files, self.max_video, [self.room.video])
        if f.get_file_size(video_list) > self.max_video_size:
            return JsonResponse(f.get_json_error_message(['動画サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_video_size, unit='MB'))]))
        self.room.video = video_list[0]
        self.room.save()

        room_imgs = self.room.roomimgs
        img_list = f.get_img_list(form_data, self.files, self.max_img, [room_imgs.img1, room_imgs.img2, room_imgs.img3, room_imgs.img4, room_imgs.img5])

        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))

        room_imgs.img1 = img_list[0]
        room_imgs.img2 = img_list[1]  
        room_imgs.img3 = img_list[2]  
        room_imgs.img4 = img_list[3]  
        room_imgs.img5 = img_list[4]  
        room_imgs.save()

        tabs = f.literal_eval(f.get_dict_item(form_data, 'tabs'))
        tab_permutation = get_object_or_404(RoomTabSequence, room=self.room, room__is_deleted=False)
        tab_permutation.tab_content1 = self.get_room_tab_title(f.get_dict_item(f.get_list_item(tabs, 0), 'content_id'), f.get_dict_item(f.get_list_item(tabs, 0), 'title'))
        tab_permutation.tab_content2 = self.get_room_tab_title(f.get_dict_item(f.get_list_item(tabs, 1), 'content_id'), f.get_dict_item(f.get_list_item(tabs, 1), 'title'))
        tab_permutation.tab_content3 = self.get_room_tab_title(f.get_dict_item(f.get_list_item(tabs, 2), 'content_id'), f.get_dict_item(f.get_list_item(tabs, 2), 'title'))
        tab_permutation.tab_content4 = self.get_room_tab_title(f.get_dict_item(f.get_list_item(tabs, 3), 'content_id'), f.get_dict_item(f.get_list_item(tabs, 3), 'title'))
        tab_permutation.tab_content5 = self.get_room_tab_title(f.get_dict_item(f.get_list_item(tabs, 4), 'content_id'), f.get_dict_item(f.get_list_item(tabs, 4), 'title'))

        self.set_tab_content_item(tab_permutation.tab_content1, f.get_dict_item(f.get_list_item(tabs, 0), 'content'))
        self.set_tab_content_item(tab_permutation.tab_content2, f.get_dict_item(f.get_list_item(tabs, 1), 'content'))
        self.set_tab_content_item(tab_permutation.tab_content3, f.get_dict_item(f.get_list_item(tabs, 2), 'content'))
        self.set_tab_content_item(tab_permutation.tab_content4, f.get_dict_item(f.get_list_item(tabs, 3), 'content'))
        self.set_tab_content_item(tab_permutation.tab_content5, f.get_dict_item(f.get_list_item(tabs, 4), 'content'))
        tab_permutation.save()

        if not f.is_empty(self.error_messages):
            return JsonResponse(f.get_json_error_message(self.error_messages))

        return JsonResponse(f.get_json_success_message(['保存しました']))

    def get_room_tab_title(self, tab_content_id, title):
        if f.is_empty(title):
            return None
        tab_content = RoomTab.objects.get_or_none(id=tab_content_id, is_deleted=False)
        if tab_content is None:
            return RoomTab.objects.create(title=title, room=self.room)
        
        if tab_content.title == title:
            return tab_content

        if tab_content.room != self.room:
            tab_content.room = self.room
        tab_content.title = title
        tab_content.save()

        return tab_content

    def set_tab_content_item(self, tab_content, data):
        if f.is_empty(tab_content):
            return False

        self.delete_tab_content(tab_content, f.get_dict_item_list(data, 'delete'))
        self.create_tab_content(tab_content, f.get_dict_item_list(data, 'create'))

    def create_tab_content(self, tab_content, tab_content_items):
        for tab_content_item in tab_content_items:
            row = f.get_dict_item(tab_content_item, 'row')
            column = f.get_dict_item(tab_content_item, 'column')
            col = f.get_dict_item(tab_content_item, 'col')
            
            if not f.is_int(row) or not f.is_int(column) or not f.is_int(col):
                raise MyBadRequest('is_int error at create_tab_content.')

            title = f.get_dict_item(tab_content_item, 'title')
            text = f.get_dict_item(tab_content_item, 'text')
            img = f.get_dict_item(tab_content_item, 'img')

            error_place = '{}行,{}列'.format(row, column)
            if len(title) > self.max_tab_title_len:
                self.error_messages.append('{} タイトルの長さが{}を超えています'.format(error_place, self.max_tab_title_len))
                continue
            if len(text) > self.max_tab_text_len:
                self.error_messages.append('{} テキストの長さが{}を超えています'.format(error_place, self.max_tab_text_len))
                continue

            if img in self.files and f.is_uploaded_file_img(self.files[img]):
                img = self.files[img]
                if not f.is_empty(img) and f.get_file_size([img]) > self.max_img_size:
                    self.error_messages.append('{} 画像サイズが{}を超えています'.format(
                        error_place, f.get_file_size_by_unit(self.max_video_size, unit='MB')))
                    continue

            if not f.is_same_empty_count([title, text, img], 2):
                raise MyBadRequest('is_same_empty error at create_tab_content.')

            items = RoomTabItem.objects.filter(
                row=row, 
                column=column, 
                tab_content_id=tab_content,
                is_deleted=False
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
                tab_content_id=tab_content
            )

        return True

    def delete_tab_content(self, tab_content, tab_content_items):
        for tab_content_item in tab_content_items:
            row = f.get_dict_item(tab_content_item, 'row')
            column = f.get_dict_item(tab_content_item, 'column')
            col = f.get_dict_item(tab_content_item, 'col')

            if not f.is_int(row) or not f.is_int(column) or not f.is_int(col):
                raise MyBadRequest('is_int error at create_tab_content.')

            items = RoomTabItem.objects.filter(
                row=row, 
                column=column,
                col=col, 
                tab_content_id=tab_content,
                is_deleted=False
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

        reply_type = get_object_or_404(RoomReplyType, room=room, room__is_deleted=False)
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
        
        rri_exist = RoomRequestInformation.objects.filter(room=room, sequence=sequence, is_deleted=False)
        if rri_exist.exists():
            rri_exist.update(is_deleted=True)

        rri = form.save(commit=False)
        rri.room = vr.get_room()
        rri.is_active = is_active
        rri.sequence = sequence
        rri.save()

        return JsonResponse(f.get_json_success_message(['保存しました']))

class RoomInformationView(TemplateView):
    model = RoomInformation

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=f.get_dict_item(kwargs, 'room_pk'), is_deleted=False)
        rris = RoomRequestInformation.objects.filter(room=room, is_deleted=False, is_active=True)
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
            
            RoomInformation.objects.create(rri=rri[0], user=self.request.user, text=value)

        return JsonResponse(f.get_json_success_message(['保存しました']))

class RoomInviteView(ManageRoomBaseView, TemplateView):
    model = User
    template_name = 'pages/manage_room.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body.decode('utf-8'))
        invite_user = get_object_or_404(User, username=f.get_dict_item(json_data, 'username'), is_active=True)
        vr = self.get_validate_room()
        room = vr.get_room()
        if RoomUser.objects.filter(user=invite_user, room=room, is_deleted=False).exists():
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

class RoomGoodView(GoodView):
    model = RoomGood
    template_name = 'pages/index_room.html'
    
    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=f.get_dict_item(kwargs, 'room_pk'), is_deleted=False)
        return JsonResponse(self.get_json_data(obj=room))

class GetRoomView(RoomItemView, TemplateView):
    model = Room

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=f.get_dict_item(kwargs, 'room_pk'), is_deleted=False)
        return JsonResponse(f.get_json_success_message(add_dict=self.get_room_item(room)))

class GetRoomRequestInformationView(TemplateView):
    model = RoomRequestInformation

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=f.get_dict_item(kwargs, 'room_pk'), is_deleted=False)
        room_base = RoomBase(room)
        return JsonResponse(f.get_json_success_message(add_dict={'rri':room_base.get_room_request_information(is_active=True)}))