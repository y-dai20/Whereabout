from django.views.generic import View, TemplateView, UpdateView, ListView
from django.db.models import F
from django.utils.timezone import make_aware, make_naive
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, Http404
from django.db.models.functions import Length

import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.models.post_models import Post, PostAgree, PostFavorite, PostDemagogy
from base.models.reply_models import ReplyPost, ReplyReply, ReplyAgree, ReplyFavorite, ReplyDemagogy, Reply2Agree, Reply2Favorite, Reply2Demagogy, ReplyPosition
from base.models.room_models import Room, RoomUser, RoomGuest, RoomInviteUser, RoomReplyType, RoomTabItem,\
    RoomGood, RoomRequestInformation, RoomInformation
from base.models.account_models import UserFollow, UserBlock, Profile
from base.models.general_models import Tag
from base.views.mixins import LoginRequiredMixin, RoomAccessRequiredMixin
from base.views.validate_views import ValidateRoomView

import json
from datetime import datetime, timedelta
from abc import abstractmethod


#todo (中) 外部キーがあるモデルはマネージャーを作成する
#todo (中) roomの親子関係を作成し、評価やユーザーを結合するなど
#todo (高) detail画面でh1などを作成して，SEO対策をする
#todo (高) sourceを画面に表示する方法を考える
class HeaderView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            admin = f.get_admin_user()
            context['other_rooms'] = Room.objects.active(admin=admin).values(
                id_=F('id'), title_=F('title'), admin_=F('admin__username'))
            return context
        
        my_rooms = Room.objects.active(admin=self.request.user).values(id_=F('id'), title_=F('title'))
        context['my_rooms'] = list(my_rooms)

        other_rooms = RoomUser.objects.active(user=self.request.user, is_blocked=False).values(
            id_=F('room__id'), title_=F('room__title'), admin_=F('room__admin__username'))
        context['other_rooms'] = other_rooms

        #todo (低) notificationをmodelとして持つべきか
        notifications = RoomGuest.objects.active(room__admin=self.request.user).count()
        notifications += RoomInviteUser.objects.active(user=self.request.user).count()
        context['notifications'] = notifications

        return context 

class IndexBaseView(HeaderView, ListView):
    template_name = 'pages/index.html'
    load_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.idx = 0
        self.is_end = False

    def post(self, request, *args, **kwargs):
        self.idx = f.get_dict_item(request.POST, 'idx')
        self.repair_idx_to_int()
        return JsonResponse(f.get_json_success_message(add_dict={'idx':self.idx+1, 'items':self.get_dump_items(), 'is_end':self.is_end}))
    
    def get_blocked_user_list(self):
        if self.request.user.is_authenticated:
            return UserBlock.objects.active(blocker=self.request.user).values_list('blockee__id', flat=True)
        return []

    def check_can_access(self, room):
        vr = ValidateRoomView(room)
        if vr.is_room_exist() and not vr.can_access(self.request.user):
            raise PermissionError('ルームに対するアクセス権がありません')

    def get_dump_items(self):
        items = self.get_items()
        if self.load_by > len(items):
            self.is_end = True
        return json.dumps(items)

    @abstractmethod
    def get_items(self):
        pass

    def get_idx_items(self, items):
        len_items = len(items)
        start_idx = self.get_start_idx()
        if start_idx > len_items:
            return []

        end_idx = self.get_end_idx()
        if end_idx > len_items:
            end_idx = len_items

        return items[start_idx : end_idx]

    def repair_idx_to_int(self):
        if type(self.idx) is int:
            return True

        if not self.idx.isdecimal():
            self.idx = 0
            return True

        self.idx = int(self.idx)
        if self.idx < 0:
            self.idx = 0
        return True

    def get_start_idx(self):
        self.repair_idx_to_int()
        return self.idx * self.load_by

    def get_end_idx(self, len_items=None):
        self.repair_idx_to_int()
        if f.is_empty(len_items):
            return (self.idx + 1) * self.load_by
        return min((self.idx + 1) * self.load_by, len_items)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dumps_object_list'] = self.get_dump_items()
        return context

class SearchBaseView(IndexBaseView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.search
        return context

    def get_params(self):
        request_params = dict(self.request.GET)
        params = {}
        for key in self.search.keys():
            if key not in request_params or f.is_empty(request_params[key][0]):
                if key == 'date_from':
                    params[key] = make_aware(datetime(2000, 1, 1))
                elif key == 'date_to':
                    params[key] = make_aware(datetime(9999, 1, 1))
                else:
                    params[key] = self.search[key]
            else:
                self.search[key] = f.get_bool_or_str(request_params[key][0])
                if key == 'date_from':
                    params[key] = make_aware(datetime.strptime(self.search[key], '%Y-%m-%d'))
                elif key == 'date_to':
                    params[key] = make_aware(datetime.strptime(self.search[key], '%Y-%m-%d') + timedelta(hours=24))
                else:
                    params[key] = self.search[key]
        return params

class ShowErrorView(TemplateView):
    template_name = 'pages/error.html'

class UpdateBaseView(LoginRequiredMixin, UpdateView):
    def __init__(self) -> None:
        super().__init__()
        self.error_messages = []

    def can_access_room(self, room):
        vr = ValidateRoomView(room)
        if not vr.is_room_exist():
            return True
        if vr.is_user_blocked(self.request.user):
            self.error_messages.append('ブロックされているため閲覧のみ可能です')
            return False
        if not vr.can_access(self.request.user):
            self.error_messages.append('アクセス制限があります')
            return False
        return True

class GoodView(UpdateBaseView):
    def get_json_data(self, obj):
        is_good = f.get_boolean_or_none(f.get_dict_item(self.request.GET, 'is_good'))
        if f.is_empty(obj) or is_good is None:
            raise MyBadRequest('good obj is empty.')

        good_obj = self.model.objects.filter(user=self.request.user, obj=obj)
        if good_obj.exists():
            if good_obj[0].is_good == is_good:
                good_obj.update(is_deleted=not good_obj[0].is_deleted)
            else:
                good_obj.update(is_good=is_good, is_deleted=False)
        else:
            good_obj.create(user=self.request.user, obj=obj, is_good=is_good)
        
        obj.good_count = self.model.objects.active(obj=obj, is_good=True).count()
        obj.bad_count = self.model.objects.active(obj=obj, is_good=False).count()
        obj.save()

        return f.get_json_success_message(add_dict={
            'is_good':is_good,
            'is_deleted':good_obj[0].is_deleted,
            'good_count':f.get_number_unit(obj.good_count),
            'bad_count':f.get_number_unit(obj.bad_count),
        })

class AgreeView(UpdateBaseView):
    def get_json_data(self, obj, room):
        is_agree = f.get_boolean_or_none(f.get_dict_item(self.request.GET, 'is_agree'))
        if f.is_empty(obj) or is_agree is None:
            raise MyBadRequest('agree obj is empty.')
        
        if not self.can_access_room(room):
            return f.get_json_error_message(self.error_messages)

        agree_obj = self.model.objects.filter(user=self.request.user, obj=obj)
        if agree_obj.exists():
            if agree_obj[0].is_agree == is_agree:
                agree_obj.update(is_deleted=not agree_obj[0].is_deleted)
            else:
                agree_obj.update(is_agree=is_agree, is_deleted=False)
        else:
            agree_obj.create(user=self.request.user, obj=obj, is_agree=is_agree)

        obj.agree_count = self.model.objects.active(obj=obj, is_agree=True).count()
        obj.disagree_count = self.model.objects.active(obj=obj, is_agree=False).count()
        obj.save()

        return f.get_json_success_message(add_dict={
            'is_agree':is_agree,
            'is_deleted':agree_obj[0].is_deleted,
            'agree_count':f.get_number_unit(obj.agree_count),
            'disagree_count':f.get_number_unit(obj.disagree_count),
        })

class DemagogyView(UpdateBaseView):
    def get_json_data(self, obj, room):
        is_true = f.get_boolean_or_none(f.get_dict_item(self.request.GET, 'is_true'))
        if f.is_empty(obj) or is_true is None:
            raise MyBadRequest('demagogy obj is empty.')

        if not self.can_access_room(room):
            return f.get_json_error_message(self.error_messages)

        demagogy = self.model.objects.filter(user=self.request.user, obj=obj)        
        if demagogy.exists():
            if demagogy[0].is_true == is_true:
                demagogy.update(is_deleted=not demagogy[0].is_deleted)
            else:
                demagogy.update(is_true=is_true, is_deleted=False)
        else:
            demagogy.create(user=self.request.user, obj=obj, is_true=is_true)
        
        obj.true_count = self.model.objects.active(obj=obj, is_true=True).count()
        obj.false_count = self.model.objects.active(obj=obj, is_true=False).count()
        obj.save()

        return f.get_json_success_message(add_dict={
            'is_true':is_true,
            'is_deleted':(demagogy[0].is_deleted),
            'true_count':f.get_number_unit(obj.true_count),
            'false_count':f.get_number_unit(obj.false_count),
        })

class FavoriteView(UpdateBaseView):
    def get_json_data(self, obj, room):
        if f.is_empty(obj):
            raise MyBadRequest('favorite obj is empty.')

        if not self.can_access_room(room):
            return f.get_json_error_message(self.error_messages)
            
        favorite = self.model.objects.filter(obj=obj, user=self.request.user)
        if favorite.exists():
            favorite.update(is_deleted=not favorite[0].is_deleted)
        else:
            favorite.create(obj=obj, user=self.request.user)

        obj.favorite_count = self.model.objects.active(obj=obj).count()
        obj.save()

        return f.get_json_success_message(add_dict={
            'is_favorite':not favorite[0].is_deleted,
            'favorite_count':f.get_number_unit(obj.favorite_count),
        })

class RoomBase(object):
    max_request_information = 10

    def __init__(self, room=None):
        self.vr = ValidateRoomView(room)
        self.room = self.vr.get_room()

    def get_room_img_paths(self):
        img_paths = []
        for img_field in self.get_room_img_list():
            img_path = f.get_img_path(img_field)
            if img_path is None:
                continue
            img_paths.append(img_path)

        return img_paths

    def get_room_img_list(self):
        if not self.vr.is_room_exist():
            return [] 

        return [self.room.img1, self.room.img2, self.room.img3, self.room.img4, self.room.img5]

    def get_room_img_size(self):
        img_sizes = []
        for img in self.get_room_img_list():
            if not bool(img):
                continue
            img_sizes.append(img.file.size)

        return img_sizes

    def get_room_tabs(self):
        if not self.vr.is_room_exist():
            return [] 

        room_tabs = []
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab1, none_val='title'))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab2))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab3))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab4))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab5))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab6))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab7))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab8))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab9))
        room_tabs.append(self.get_room_tab(self.room.roomtabsequence.tab10))

        return room_tabs

    def get_room_tab(self, room_tab, none_val=None):
        return {'id':room_tab.id, 'title':room_tab.title} if room_tab else {'id':'', 'title':none_val}

    def get_room_tab_items(self, room_tab):
        return list(RoomTabItem.objects.active(room_tab=room_tab)
                .order_by('row', 'column').values('title', 'text', 'img', 'row', 'column', 'col'))

    def get_room_reply_types(self, is_unique=True):
        if not self.vr.is_room_exist():
            return f.get_reply_types()

        reply_type_obj = f.get_object_or_404_from_q(RoomReplyType.objects.active(room=self.room))
        reply_types = [
            reply_type_obj.type1,
            reply_type_obj.type2,
            reply_type_obj.type3,
            reply_type_obj.type4,
            reply_type_obj.type5,
            reply_type_obj.type6,
            reply_type_obj.type7,
            reply_type_obj.type8,
            reply_type_obj.type9,
            reply_type_obj.type10,
        ]
        if is_unique:
            return list(sorted(set(reply_types), key=reply_types.index))

        return reply_types

    def get_room_tags(self):
        if not self.vr.is_room_exist() or self.room.tag_sequence is None:
            return []

        room_tags = [
            self.room.tag_sequence.tag1.name if self.room.tag_sequence.tag1 is not None else '',
            self.room.tag_sequence.tag2.name if self.room.tag_sequence.tag2 is not None else '',
            self.room.tag_sequence.tag3.name if self.room.tag_sequence.tag3 is not None else '',
            self.room.tag_sequence.tag4.name if self.room.tag_sequence.tag4 is not None else '',
            self.room.tag_sequence.tag5.name if self.room.tag_sequence.tag5 is not None else '',
            self.room.tag_sequence.tag6.name if self.room.tag_sequence.tag6 is not None else '',
            self.room.tag_sequence.tag7.name if self.room.tag_sequence.tag7 is not None else '',
            self.room.tag_sequence.tag8.name if self.room.tag_sequence.tag8 is not None else '',
            self.room.tag_sequence.tag9.name if self.room.tag_sequence.tag9 is not None else '',
            self.room.tag_sequence.tag10.name if self.room.tag_sequence.tag10 is not None else '',
        ]

        return room_tags

    def get_room_request_information(self, is_active=None):
        if not self.vr.is_room_exist():
            return []

        rri_list = [None for _ in range(self.max_request_information)]
        is_active = f.get_boolean_or_none(is_active)
        if is_active is None:
            rri_objects = RoomRequestInformation.objects.active(room=self.room).values(
                'id', 'sequence', 'title', 'type', 'choice', 'min_length', 'max_length', 'is_active', 'is_deleted')
        else:
            rri_objects = RoomRequestInformation.objects.active(room=self.room, is_active=is_active).values(
                'id', 'sequence', 'title', 'type', 'choice', 'min_length', 'max_length', 'is_active', 'is_deleted')

        for rri_object in rri_objects:
            idx = rri_object['sequence'] - 1
            if idx < 0 or self.max_request_information < idx:
                raise ValueError()
            rri_list[idx] = rri_object

        return rri_list

    @staticmethod
    def get_my_room_list(user):
        if not f.is_empty(user) and user.is_authenticated:
            return list(Room.objects.active(admin=user).values_list('id', flat=True))
        
        return []

    @staticmethod
    def get_attend_room_list(user):
        if not f.is_empty(user) and user.is_authenticated:
            return list(RoomUser.objects.active(is_blocked=False, user=user).values_list('room', flat=True))
        return []

    @staticmethod
    def get_other_room_list(rooms=[]):
        return list(Room.objects.active().public().exclude(id__in=rooms).values_list('id', flat=True))

class RoomItemView(View):

    def get_room_items(self, rooms):
        queryset = []
        for room in rooms:
            queryset.append(self.get_room_item(room))
        return queryset

    def get_room_item(self, room):
        vr = ValidateRoomView(room)
        if not vr.is_room_exist():
            return {}

        room = vr.get_room()
        user = self.request.user if self.request.user.is_authenticated else None
        user_good = RoomGood.objects.active(obj=room, user=user).values('is_good')
        room_base = RoomBase(room)
        room_dict = {
            'id':room.id,
            'title':room.title,
            'subtitle':room.subtitle,
            'admin':room.admin.username,
            'admin_img':f.get_img_path(room.admin.profile.img),
            'user_count':f.get_number_unit(room.participant_count),
            'img_paths':room_base.get_room_img_paths(),
            'room_tags':room_base.get_room_tags(),
            'video_path':f.get_img_path(room.video),
            'created_at':f.get_display_datetime(datetime.now() - make_naive(room.created_at)),
            'good_count':f.get_number_unit(room.good_count),
            'bad_count':f.get_number_unit(room.bad_count),
            'good_state':user_good[0]['is_good'] if user_good.exists() else None,
        }
        
        return room_dict

#todo (中) sourceの値が内部か外部かで色・挙動を変えたい
class PostItemView(View):

    def get_post_items(self, posts):
        queryset = []
        for post in posts:
            queryset.append(self.get_post_item(post))
        return queryset

    def get_post_item(self, post):
        if not isinstance(post, Post):
            return {}
        
        user = self.request.user if self.request.user.is_authenticated else None
        user_agree = PostAgree.objects.active(obj=post, user=user).values('is_agree')
        user_demagogy = PostDemagogy.objects.active(obj=post, user=user).values('is_true')        
        favorite_state = PostFavorite.objects.active(obj=post, user=user)
        img_paths = []
        for img_field in [post.img1, post.img2, post.img3, post.img4]:
                img_paths.append(f.get_img_path(img_field))
        
        post_dict = {
            'obj_type':'post',
            'obj_id':post.id,
            'room_id':None,
            'title':post.title,
            'text':post.text,
            'source':post.source,
            'img_paths':img_paths,
            'video_path':f.get_img_path(post.video),
            'username':post.user.username,
            'user_img':f.get_img_path(post.user.profile.img),
            'created_at':f.get_display_datetime(datetime.now() - make_naive(post.created_at)),
            'agree_count':f.get_number_unit(post.agree_count),
            'disagree_count':f.get_number_unit(post.disagree_count),
            'agree_state':user_agree[0]['is_agree'] if user_agree.exists() else None,
            'reply_count':f.get_number_unit(post.reply_count),
            'favorite_state':favorite_state.exists(),
            'favorite_count':f.get_number_unit(post.favorite_count),
            'true_count':f.get_number_unit(post.true_count),
            'false_count':f.get_number_unit(post.false_count),
            'demagogy_state':user_demagogy[0]['is_true'] if user_demagogy.exists() else None,
            'can_user_delete':post.user == user,
            'post_tags':self.get_post_tags(post),
        }

        if post.room is not None:
            post_dict['room_title'] = post.room.title
            post_dict['room_id'] = post.room.id
            post_dict['can_user_delete'] =(post.room.admin == user)

        return post_dict
    
    def get_post_tags(self, post):
        if f.is_empty(post) or post.tag_sequence is None:
            return []

        tags = [
            post.tag_sequence.tag1.name if post.tag_sequence.tag1 is not None else '',
            post.tag_sequence.tag2.name if post.tag_sequence.tag2 is not None else '',
            post.tag_sequence.tag3.name if post.tag_sequence.tag3 is not None else '',
            post.tag_sequence.tag4.name if post.tag_sequence.tag4 is not None else '',
            post.tag_sequence.tag5.name if post.tag_sequence.tag5 is not None else '',
        ]

        return tags


class UserItemView(View):

    def get_user_items(self, profiles):
        queryset = []
        for profile in profiles:
            queryset.append(self.get_user_item(profile))
        return queryset

    def get_user_item(self, profile):
        if not isinstance(profile, Profile):
            return {}
            
        user_dict = f.get_json_success_message(add_dict={
            'username':profile.user.username,
            'created_at':f.get_display_datetime(datetime.now() - make_naive(profile.user.created_at)),
            'img':f.get_img_path(profile.img),
            'user_tags':self.get_profile_tags(profile),
            'user_rooms':list(Room.objects.active(admin=profile.user).public().values(id_=F('id'), title_=F('title'))),
            'profession':profile.profession,
            'description':profile.description,
            'followed_count':f.get_number_unit(profile.followed_count),
            'blocked_count':f.get_number_unit(profile.blocked_count),
        })

        if not self.request.user.is_authenticated:
            return user_dict

        user_dict['is_follow'] = UserFollow.objects.active(followee=profile.user, follower=self.request.user).exists()
        user_dict['is_block'] = UserBlock.objects.active(blockee=profile.user, blocker=self.request.user).exists()

        return user_dict

    def get_profile_tags(self, profile):
        if f.is_empty(profile) or profile.tag_sequence is None:
            return []

        tags = [
            profile.tag_sequence.tag1.name if profile.tag_sequence.tag1 is not None else '',
            profile.tag_sequence.tag2.name if profile.tag_sequence.tag2 is not None else '',
            profile.tag_sequence.tag3.name if profile.tag_sequence.tag3 is not None else '',
            profile.tag_sequence.tag4.name if profile.tag_sequence.tag4 is not None else '',
            profile.tag_sequence.tag5.name if profile.tag_sequence.tag5 is not None else '',
        ]

        return tags

class ReplyItemView(View):

    def get_reply_items(self, replies):
        queryset = []
        for reply in replies:
            queryset.append(self.get_reply_item(reply))
        return queryset

    def get_reply_item(self, reply):
        if not isinstance(reply, ReplyPost):
            return {}

        user = self.request.user if self.request.user.is_authenticated else None
        user_agree = ReplyAgree.objects.active(obj=reply, user=user).values('is_agree')
        user_demagogy = ReplyDemagogy.objects.active(obj=reply, user=user).values('is_true')
        favorite_state = ReplyFavorite.objects.active(obj=reply, user=user)

        vr = ValidateRoomView(reply.post.room)
        room_base = RoomBase(vr.get_room())
        dict_queryset = {
            'obj_type':'reply',
            'obj_id':reply.id,
            'room_id':None,
            'post_id':reply.post.id,
            'source':reply.source,
            'reply_count':f.get_number_unit(reply.reply_count),
            'text':reply.text,
            'username':reply.user.username,
            'user_img':f.get_img_path(reply.user.profile.img),
            'type':reply.type,
            'type_id':f.get_list_index(room_base.get_room_reply_types(), reply.type),
            'is_agree':True if reply.position == ReplyPosition.AGREE else False,
            'is_neutral':True if reply.position == ReplyPosition.NEUTRAL else False,
            'is_disagree':True if reply.position == ReplyPosition.DISAGREE else False,
            'created_at':f.get_display_datetime(datetime.now() - make_naive(reply.created_at)),
            'img_path':f.get_img_path(reply.img) if not f.is_empty(reply.img) else '',
            'agree_count':f.get_number_unit(reply.agree_count),
            'disagree_count':f.get_number_unit(reply.disagree_count),
            'agree_state': user_agree[0]['is_agree'] if user_agree.exists() else None,
            'true_count':f.get_number_unit(reply.true_count),
            'false_count':f.get_number_unit(reply.false_count),
            'demagogy_state':user_demagogy[0]['is_true'] if user_demagogy.exists() else None,
            'favorite_state':favorite_state.exists(),
            'favorite_count':f.get_number_unit(reply.favorite_count),
            'can_user_delete':reply.user == user,
        }

        if vr.is_room_exist():
            dict_queryset['can_user_delete'] = vr.is_admin(user)
            dict_queryset['room_id'] = reply.post.room.id

        return dict_queryset

class Reply2ItemView(View):

    def get_reply2_items(self, reply2):
        queryset = []
        for reply in reply2:
            queryset.append(self.get_reply2_item(reply))
        return queryset

    def get_reply2_item(self, reply2):
        if not isinstance(reply2, ReplyReply):
            return {}

        user = self.request.user if self.request.user.is_authenticated else None
        user_agree = Reply2Agree.objects.active(obj=reply2, user=user).values('is_agree')
        user_demagogy = Reply2Demagogy.objects.active(obj=reply2, user=user).values('is_true')
        favorite_state = Reply2Favorite.objects.active(obj=reply2, user=user)

        vr = ValidateRoomView(reply2.reply.post.room)
        room_base = RoomBase(vr.get_room())
        dict_queryset = {
            'obj_type':'reply2',
            'obj_id':reply2.id,
            'room_id':None,
            'reply_id':reply2.reply.id,
            'text':reply2.text,
            'source':reply2.source,
            'username':reply2.user.username,
            'user_img':f.get_img_path(reply2.user.profile.img),
            'type':reply2.type,
            'type_id':f.get_list_index(room_base.get_room_reply_types(), reply2.type),
            'is_agree':True if reply2.position == ReplyPosition.AGREE else False,
            'is_neutral':True if reply2.position == ReplyPosition.NEUTRAL else False,
            'is_disagree':True if reply2.position == ReplyPosition.DISAGREE else False,
            'created_at':f.get_display_datetime(datetime.now() - make_naive(reply2.created_at)),
            'img_path':f.get_img_path(reply2.img) if not f.is_empty(reply2.img) else '',
            'agree_count':f.get_number_unit(reply2.agree_count),
            'disagree_count':f.get_number_unit(reply2.disagree_count),
            'agree_state': user_agree[0]['is_agree'] if user_agree.exists() else None,
            'true_count':f.get_number_unit(reply2.true_count),
            'false_count':f.get_number_unit(reply2.false_count),
            'demagogy_state':user_demagogy[0]['is_true'] if user_demagogy.exists() else None,
            'favorite_state':favorite_state.exists(),
            'favorite_count':f.get_number_unit(reply2.favorite_count),
            'can_user_delete':reply2.user == user,
        }

        if vr.is_room_exist():
            dict_queryset['can_user_delete'] = vr.is_admin(user)

        return dict_queryset

class DetailBaseView(SearchBaseView):
    load_by = 20

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.search = {
            'username':'',
            'text': '',
            'date_from':'', 
            'date_to':'', 
            'position':'',
            'type':'',
            'order':'',
        }
        self.order = {
            'created_at':True,
            'reaction_count':False,
            'favorite_count':False,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def get_replies_after_order(self, replies):
        params = self.get_params()
        if params['order'] not in self.order.keys():
            return replies

        for key in self.order.keys():
            self.order[key] = False
        self.order[params['order']] = True

        if self.order['favorite_count']:
            return replies.order_by('-favorite_count')
        if self.order['reaction_count']:
            return replies.annotate(reaction_count=F('agree_count')+F('disagree_count')).order_by('-reaction_count')
        
        return replies

class ShowRoomBaseView(RoomAccessRequiredMixin, HeaderView):
    def validate_room(self):
        self.vr = ValidateRoomView(f.get_dict_item(self.kwargs, 'room_pk'))
        self.room = self.vr.get_room()
        self.room_base = RoomBase(self.room)

    def get(self, request, *args, **kwargs):
        self.validate_room()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.validate_room()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        room = self.room
        context['room_id'] = room.id
        context['title'] = room.title
        context['subtitle'] = room.subtitle
        context['is_public'] = room.is_public
        context['need_approval'] = room.need_approval

        context['video_path'] = f.get_img_path(room.video)
        context['img_paths'] = self.room_base.get_room_img_paths()
        context['room_tabs'] = self.room_base.get_room_tabs()
        context['room_tab_items'] = self.room_base.get_room_tab_items(self.room.roomtabsequence.tab1)
        context['request_information'] = self.room_base.get_room_request_information()
        context['room_tags'] = self.room_base.get_room_tags()

        #todo (高) 住所の表示方法について
        if self.room.personal is not None:
            context['web'] = self.room.personal.web
            context['web_domain'] = f.get_domain(self.room.personal.web)
            context['phone'] = self.room.personal.phone
            context['zip_code'] = self.room.personal.zip_code
            context['state'] = self.room.personal.state
            context['city'] = self.room.personal.city
            context['address_1'] = self.room.personal.address_1
            context['address_2'] = self.room.personal.address_2
            context['mon_from'] = self.room.personal.mon_from
            context['mon_to'] = self.room.personal.mon_to
            context['tue_from'] = self.room.personal.tue_from
            context['tue_to'] = self.room.personal.tue_to
            context['wed_from'] = self.room.personal.wed_from
            context['wed_to'] = self.room.personal.wed_to
            context['thu_from'] = self.room.personal.thu_from
            context['thu_to'] = self.room.personal.thu_to
            context['fri_from'] = self.room.personal.fri_from
            context['fri_to'] = self.room.personal.fri_to
            context['sat_from'] = self.room.personal.sat_from
            context['sat_to'] = self.room.personal.sat_to
            context['sun_from'] = self.room.personal.sun_from
            context['sun_to'] = self.room.personal.sun_to


        context['do_pass_request_information'] = False
        if not self.vr.is_admin(self.request.user) and\
            self.vr.is_room_user(self.request.user) and\
                not RoomInformation.objects.active(rri__room=room, user=self.request.user).exists():
            context['do_pass_request_information'] = True
        
        profile = room.admin.profile
        context['admin_img'] = f.get_img_path(profile.img)
        context['username'] = profile.user.username
        context['profession'] = profile.profession
        context['description'] = profile.description

        if not self.request.user.is_authenticated:
            return context

        if self.vr.is_admin(self.request.user):
            context['is_admin'] = True
            return context

        #todo (低) 基本的にobjects.filterは共通で書くようにする
        room_user = f.get_from_queryset(RoomUser.objects.active(room=room, user=self.request.user))
        if room_user is not None:
            if room_user.is_blocked:
                context['is_blocked'] = True
            else:
                context['is_room_user'] = True
            return context
        
        room_guest = f.get_from_queryset(RoomGuest.objects.active(room=room, guest=self.request.user))
        if room_guest is not None:
            context['is_waiting'] = True
    
        return context

class SendMailView(TemplateView):
    user_from = settings.EMAIL_HOST_USER
    one_time_id_len = 128

    def send_mail(self, title, message, user_to):
        send_mail(
            title,
            message,
            self.user_from,
            user_to,
            fail_silently=False, 
        )

    def get_base_path(self):
        return settings.MY_URL

    def get_success_json_response(self):
        return JsonResponse(f.get_json_success_message(['メールを送信しました']))

    def get_one_time_id(self):
        return f.create_id(self.one_time_id_len)

class DeleteBaseView(TemplateView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def validate_delete(self, room, user):
        vr = ValidateRoomView(room)
        if (vr.is_room_exist() and not vr.is_admin(self.request.user)) or self.request.user != user:
            raise MyBadRequest('no permission to delete.')

class GetTag(TemplateView):
    def post(self, request, *args, **kwargs):
        tag = f.get_dict_item(request.POST, 'tag')

        candidates = Tag.objects.active(name__contains=tag).order_by(Length('name')).values_list('name')
        return JsonResponse({'candidates':list(candidates)})