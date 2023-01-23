from django.views.generic import View, TemplateView, UpdateView, ListView
from django.db.models import F
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import make_aware, make_naive
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.http import JsonResponse, Http404


from base.views.exceptions import MyBadRequest
from base.models.post_models import Post, PostImgs, PostAgree, PostFavorite, PostDemagogy
from base.models.reply_models import ReplyAgree, ReplyFavorite, ReplyDemagogy, Reply2Agree, Reply2Favorite, Reply2Demagogy, ReplyPosition
from base.models.room_models import Room, RoomUser, RoomGuest, RoomInviteUser, RoomReplyType, TabContentItem,\
    TabPermutation, RoomGood, RoomRequestInformation, RoomInformation
from base.models.account_models import UserFollow, UserBlock, Profile
from base.views.functions import get_number_unit, get_bool_or_str, get_list_index,\
    get_img_path, get_dict_item, is_empty, get_json_error_message, get_json_success_message,\
    get_reply_types, get_boolean_or_none, get_display_datetime
from base.views.mixins import LoginRequiredMixin
from base.views.validate_views import ValidateRoomView

import json
from datetime import datetime, timedelta
from abc import abstractmethod

class HeaderView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context
        
        my_rooms = Room.objects.filter(admin=self.request.user, is_deleted=False).values(id_=F('id'), title_=F('title'))
        context['my_rooms'] = my_rooms

        other_rooms = RoomUser.objects.filter(user=self.request.user, is_deleted=False, is_blocked=False).values(
            id_=F('room__id'), title_=F('room__title'), admin_=F('room__admin__username'))
        context['other_rooms'] = other_rooms

        # todo (低) notificationをmodelとして持つべきか
        notifications = RoomGuest.objects.filter(room__admin=self.request.user, is_deleted=False).count()
        notifications += RoomInviteUser.objects.filter(user=self.request.user, is_deleted=False).count()
        context['notifications'] = notifications

        return context 

class IndexBaseView(HeaderView, ListView):
    template_name = 'pages/index.html'
    load_by = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.idx = 0
        self.items = []

    def post(self, request, *args, **kwargs):
        self.idx = get_dict_item(request.POST, 'idx')
        if not self.idx.isdecimal():
            self.idx = 0

        self.idx = int(self.idx)
        if self.idx < 0:
            self.idx = 0

        return JsonResponse(get_json_success_message(add_dict={'idx':self.idx+1, 'items':self.get_dump_items(), 'is_end':True if is_empty(self.items) else False}))
    
    def get_blocked_user_list(self):
        if self.request.user.is_authenticated:
            return UserBlock.objects.filter(blocker=self.request.user ,is_deleted=False).values_list('blockee__id', flat=True)
        return []

    def get_dump_items(self):
        self.items = self.get_items()
        return json.dumps(self.items)

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

    def get_start_idx(self):
        return self.idx * self.load_by

    def get_end_idx(self, len_items=None):
        if is_empty(len_items):
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
            if key not in request_params or is_empty(request_params[key][0]):
                if key == 'date_from':
                    params[key] = make_aware(datetime(2000, 1, 1))
                elif key == 'date_to':
                    params[key] = make_aware(datetime(9999, 1, 1))
                else:
                    params[key] = ''
            else:
                self.search[key] = get_bool_or_str(request_params[key][0])
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
        is_good = get_boolean_or_none(get_dict_item(self.request.GET, 'is_good'))
        if is_empty(obj) or is_good is None:
            raise MyBadRequest('good obj is empty.')

        good_obj = self.model.objects.filter(user=self.request.user, obj=obj)
        if good_obj.exists():
            if good_obj[0].is_good == is_good:
                good_obj.update(is_deleted=not good_obj[0].is_deleted)
            else:
                good_obj.update(is_good=is_good, is_deleted=False)
        else:
            good_obj.create(user=self.request.user, obj=obj, is_good=is_good)
        
        obj.good_count = self.model.objects.filter(obj=obj, is_good=True, is_deleted=False).count()
        obj.bad_count = self.model.objects.filter(obj=obj, is_good=False, is_deleted=False).count()
        obj.save()

        return get_json_success_message(add_dict={
            'is_good':is_good,
            'is_deleted':good_obj[0].is_deleted,
            'good_count':get_number_unit(obj.good_count),
            'bad_count':get_number_unit(obj.bad_count),
        })

class AgreeView(UpdateBaseView):
    def get_json_data(self, obj, room):
        is_agree = get_boolean_or_none(get_dict_item(self.request.GET, 'is_agree'))
        if is_empty(obj) or is_agree is None:
            raise MyBadRequest('agree obj is empty.')
        
        if not self.can_access_room(room):
            return get_json_error_message(self.error_messages)

        agree_obj = self.model.objects.filter(user=self.request.user, obj=obj)
        if agree_obj.exists():
            if agree_obj[0].is_agree == is_agree:
                agree_obj.update(is_deleted=not agree_obj[0].is_deleted)
            else:
                agree_obj.update(is_agree=is_agree, is_deleted=False)
        else:
            agree_obj.create(user=self.request.user, obj=obj, is_agree=is_agree)

        obj.expansion.agree_count = self.model.objects.filter(obj=obj, is_agree=True, is_deleted=False).count()
        obj.expansion.disagree_count = self.model.objects.filter(obj=obj, is_agree=False, is_deleted=False).count()
        obj.expansion.save()

        return get_json_success_message(add_dict={
            'is_agree':is_agree,
            'is_deleted':agree_obj[0].is_deleted,
            'agree_count':get_number_unit(obj.expansion.agree_count),
            'disagree_count':get_number_unit(obj.expansion.disagree_count),
        })

class DemagogyView(UpdateBaseView):
    def get_json_data(self, obj, room):
        is_true = get_boolean_or_none(get_dict_item(self.request.GET, 'is_true'))
        if is_empty(obj) or is_true is None:
            raise MyBadRequest('demagogy obj is empty.')

        if not self.can_access_room(room):
            return get_json_error_message(self.error_messages)

        demagogy = self.model.objects.filter(user=self.request.user, obj=obj)        
        if demagogy.exists():
            if demagogy[0].is_true == is_true:
                demagogy.update(is_deleted=not demagogy[0].is_deleted)
            else:
                demagogy.update(is_true=is_true, is_deleted=False)
        else:
            demagogy.create(user=self.request.user, obj=obj, is_true=is_true)
        
        obj.expansion.true_count = self.model.objects.filter(obj=obj, is_true=True, is_deleted=False).count()
        obj.expansion.false_count = self.model.objects.filter(obj=obj, is_true=False, is_deleted=False).count()
        obj.expansion.save()

        return get_json_success_message(add_dict={
            'is_true':is_true,
            'is_deleted':(demagogy[0].is_deleted),
            'true_count':get_number_unit(obj.expansion.true_count),
            'false_count':get_number_unit(obj.expansion.false_count),
        })

class FavoriteView(UpdateBaseView):
    def get_json_data(self, obj, room):
        if is_empty(obj):
            raise MyBadRequest('favorite obj is empty.')

        if not self.can_access_room(room):
            return get_json_error_message(self.error_messages)
            
        favorite = self.model.objects.filter(obj=obj, user=self.request.user)
        if favorite.exists():
            favorite.update(is_deleted=not favorite[0].is_deleted)
        else:
            favorite.create(obj=obj, user=self.request.user)

        obj.expansion.favorite_count = self.model.objects.filter(obj=obj, is_deleted=False).count()
        obj.expansion.save()

        return get_json_success_message(add_dict={
            'is_favorite':not favorite[0].is_deleted,
            'favorite_count':get_number_unit(obj.expansion.favorite_count),
        })

class RoomBase(object):
    max_request_information = 10

    def __init__(self, room=None):
        self.vr = ValidateRoomView(room)
        self.room = self.vr.get_room()

    def get_room_img_paths(self):
        img_paths = []
        for img_field in self.get_room_img_list():
            img_path = get_img_path(img_field)
            if img_path is None:
                continue
            img_paths.append(img_path)

        return img_paths

    def get_room_img_list(self):
        if not self.vr.is_room_exist():
            return [] 
        room_imgs = self.room.roomimgs
        return [room_imgs.img1, room_imgs.img2, room_imgs.img3, room_imgs.img4, room_imgs.img5]

    def get_room_img_size(self):
        img_sizes = []
        for img in self.get_room_img_list():
            if not bool(img):
                continue
            img_sizes.append(img.file.size)

        return img_sizes

    def get_tab_contents(self):
        if not self.vr.is_room_exist():
            return [] 

        tab_titles = []
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content1, none_val='title'))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content2))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content3))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content4))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content5))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content6))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content7))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content8))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content9))
        tab_titles.append(self.get_tab_content(self.room.tabpermutation.tab_content10))

        return tab_titles

    def get_tab_content(self, tab_content, none_val=None):
        return {'id':tab_content.id, 'title':tab_content.title} if tab_content else {'id':'', 'title':none_val}

    def get_tab_content_items(self, tab_content_id):
        return list(TabContentItem.objects.filter(
            tab_content_id=tab_content_id, 
            is_deleted=False
            ).order_by('row', 'column').values('title', 'text', 'img', 'row', 'column', 'col'))

    def get_room_reply_types(self, is_unique=True):
        if not self.vr.is_room_exist():
            return get_reply_types()

        reply_type_obj = get_object_or_404(RoomReplyType, room=self.room, room__is_deleted=False)
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

    def get_room_request_information(self, is_active=None):
        if not self.vr.is_room_exist():
            return []

        rri_list = [None for _ in range(self.max_request_information)]
        is_active = get_boolean_or_none(is_active)
        if is_active is None:
            rri_objects = RoomRequestInformation.objects.filter(room=self.room, is_deleted=False).values(
                'id', 'sequence', 'title', 'type', 'choice', 'min_length', 'max_length', 'is_active', 'is_deleted')
        else:
            rri_objects = RoomRequestInformation.objects.filter(room=self.room, is_active=is_active, is_deleted=False).values(
                'id', 'sequence', 'title', 'type', 'choice', 'min_length', 'max_length', 'is_active', 'is_deleted')

        for rri_object in rri_objects:
            idx = rri_object['sequence'] - 1
            if idx < 0 or self.max_request_information < idx:
                raise ValueError()
            rri_list[idx] = rri_object

        return rri_list

    @staticmethod
    def get_my_room_list(user):
        if not is_empty(user) and user.is_authenticated:
            return list(Room.objects.filter(is_deleted=False, admin=user).values_list('id', flat=True))
        
        return []

    @staticmethod
    def get_attend_room_list(user):
        if not is_empty(user) and user.is_authenticated:
            return list(RoomUser.objects.filter(is_deleted=False, is_blocked=False, user=user).values_list('room', flat=True))
        return []

    @staticmethod
    def get_other_room_list(rooms=[]):
        return list(Room.objects.filter(is_deleted=False, is_public=True).exclude(id__in=rooms).values_list('id', flat=True))

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
        user_good = RoomGood.objects.filter(obj=room, user=self.request.user, is_deleted=False).values('is_good')
        room_base = RoomBase(room)
        room_dict = {
            'id':room.id,
            'title':room.title,
            'subtitle':room.subtitle,
            'admin':room.admin.username,
            'admin_img':get_img_path(room.admin.profile.img),
            'user_count':get_number_unit(room.participant_count),
            'img_paths':room_base.get_room_img_paths(),
            'video_path':get_img_path(room.video),
            'created_at':get_display_datetime(datetime.now() - make_naive(room.created_at)),
            'good_count':get_number_unit(room.good_count),
            'bad_count':get_number_unit(room.bad_count),
            'good_state':user_good[0]['is_good'] if user_good.exists() else None,
        }
        
        return room_dict

class PostItemView(View):

    def get_post_items(self, posts):
        queryset = []
        for post in posts:
            queryset.append(self.get_post_item(post))
        return queryset

    def get_post_item(self, post):
        if not isinstance(post, Post):
            return {}
        
        user_agree = PostAgree.objects.filter(obj=post, user=self.request.user, is_deleted=False).values('is_agree')
        user_demagogy = PostDemagogy.objects.filter(obj=post, user=self.request.user, is_deleted=False).values('is_true')        
        favorite_state = PostFavorite.objects.filter(obj=post, user=self.request.user, is_deleted=False)
        post_imgs = PostImgs.objects.filter(post=post)
        img_paths = []
        if post_imgs.exists():
            for img_field in [post_imgs[0].img1, post_imgs[0].img2, post_imgs[0].img3, post_imgs[0].img4]:
                img_paths.append(get_img_path(img_field))
        
        post_dict = {
            'obj_type':'post',
            'obj_id':post.id,
            'title':post.title,
            'text':post.text,
            'img_paths':img_paths,
            'video_path':get_img_path(post.video),
            'username':post.user.username,
            'user_img':get_img_path(post.user.profile.img),
            'created_at':get_display_datetime(datetime.now() - make_naive(post.created_at)),
            'agree_count':get_number_unit(post.expansion.agree_count),
            'disagree_count':get_number_unit(post.expansion.disagree_count),
            'agree_state':user_agree[0]['is_agree'] if user_agree.exists() else None,
            'reply_count':get_number_unit(post.expansion.reply_count),
            'favorite_state':favorite_state.exists(),
            'favorite_count':get_number_unit(post.expansion.favorite_count),
            'true_count':get_number_unit(post.expansion.true_count),
            'false_count':get_number_unit(post.expansion.false_count),
            'demagogy_state':user_demagogy[0]['is_true'] if user_demagogy.exists() else None,
            'can_user_delete':post.user == self.request.user
        }

        if post.room is not None:
            post_dict['room_title'] = post.room.title
            post_dict['room_id'] = post.room.id
            post_dict['can_user_delete'] =(post.room.admin == self.request.user)

        return post_dict

class UserItemView(View):

    def get_user_item(self, profile):
        if not isinstance(profile, Profile):
            return {}
            
        user_dict = get_json_success_message(add_dict={
            'username':profile.user.username,
            'created_at':get_display_datetime(datetime.now() - make_naive(profile.user.created_at)),
            'img':get_img_path(profile.img),
            'profession':profile.profession,
            'description':profile.description,
            'followed_count':get_number_unit(profile.followed_count),
            'blocked_count':get_number_unit(profile.blocked_count),
        })

        if not self.request.user.is_authenticated:
            return user_dict

        user_dict['is_follow'] = UserFollow.objects.filter(followee=profile.user, is_deleted=False, follower=self.request.user).exists()
        user_dict['is_block'] = UserBlock.objects.filter(blockee=profile.user, is_deleted=False, blocker=self.request.user).exists()

        return user_dict

    def get_user_items(self, profiles):
        queryset = []
        for profile in profiles:
            queryset.append(self.get_user_item(profile))
        return queryset

#todo (中) SearchBaseViewを継承させる？
#todo (中) 要確認，DetailItemViewを別で作った方がいいかもしれない
class DetailBaseView(PostItemView):
    load_by = 3

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.room = None
        self.search = {
            'username':'',
            'text': '',
            'date_from':'', 
            'date_to':'', 
            'position':'',
            'type':'',
        }
        self.order = {
            'created_at':True,
            'reaction_count':False,
            'favorite_count':False,
        }

    def check_can_access(self, room):
        vr = ValidateRoomView(room)
        if vr.is_room_exist() and not vr.can_access(self.request.user):
            raise PermissionError('ルームに対するアクセス権がありません')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        
        #todo (高) self.roomをどこで入れているのかわからなくない？
        vr = ValidateRoomView(self.room)
        if not vr.is_room_exist() or not self.request.user.is_authenticated:
            return context
            
        if vr.is_admin(self.request.user):
            context['is_allowed'] = True
            context['is_admin'] = True
            return context

        if vr.is_room_user(self.request.user):
            context['is_allowed'] = False

        return context

    def get_post_detail_items(self, reply_posts):
        queryset = []
        for reply in reply_posts:
            queryset.append(self.get_post_detail_item(reply))
        return queryset

    def get_post_detail_item(self, reply_post):
        if is_empty(reply_post):
            return {}

        self.agree_model = ReplyAgree
        self.demagogy_model = ReplyDemagogy
        self.favorite_model = ReplyFavorite

        dict_queryset = self.get_detail_item(reply_post, reply_post.post.room)
        dict_queryset['obj_type'] = 'reply'
        dict_queryset['obj_id'] = reply_post.id
        dict_queryset['post_id'] = reply_post.post.id
        dict_queryset['url'] = reply_post.url
        dict_queryset['reply_count'] = get_number_unit(reply_post.expansion.reply_count)
        if not is_empty(reply_post.post.room):        
            dict_queryset['room_id'] = reply_post.post.room.id
        return dict_queryset

    def get_reply_detail_items(self, reply2):
        queryset = []
        for reply in reply2:
            queryset.append(self.get_reply_detail_item(reply))
        return queryset

    def get_reply_detail_item(self, reply2):
        if is_empty(reply2):
            return {}

        self.agree_model = Reply2Agree
        self.demagogy_model = Reply2Demagogy
        self.favorite_model = Reply2Favorite

        dict_queryset = self.get_detail_item(reply2, reply2.reply.post.room)
        dict_queryset['obj_type'] = 'reply2'
        dict_queryset['obj_id'] = reply2.id
        
        return dict_queryset
    
    def get_detail_item(self, obj, room=None):
        user_agree = self.agree_model.objects.filter(obj=obj.id, user=self.request.user, is_deleted=False).values('is_agree')
        user_demagogy = self.demagogy_model.objects.filter(obj=obj, user=self.request.user, is_deleted=False).values('is_true')
        favorite_state = self.favorite_model.objects.filter(obj=obj.id, user=self.request.user, is_deleted=False)

        room_base = RoomBase(room)
        dict_queryset = {
            'text':obj.text,
            'username':obj.user.username,
            'user_img':get_img_path(obj.user.profile.img),
            'type':obj.type,
            'type_id':get_list_index(room_base.get_room_reply_types(), obj.type),
            'is_agree':True if obj.position == ReplyPosition.AGREE else False,
            'is_neutral':True if obj.position == ReplyPosition.NEUTRAL else False,
            'is_disagree':True if obj.position == ReplyPosition.DISAGREE else False,
            'created_at':get_display_datetime(datetime.now() - make_naive(obj.created_at)),
            'img_path':get_img_path(obj.img) if not is_empty(obj.img) else '',

            'agree_count':get_number_unit(obj.expansion.agree_count),
            'disagree_count':get_number_unit(obj.expansion.disagree_count),
            'agree_state': user_agree[0]['is_agree'] if user_agree.exists() else None,

            'true_count':get_number_unit(obj.expansion.true_count),
            'false_count':get_number_unit(obj.expansion.false_count),
            'demagogy_state':user_demagogy[0]['is_true'] if user_demagogy.exists() else None,

            'favorite_state':favorite_state.exists(),
            'favorite_count':get_number_unit(obj.expansion.favorite_count),

            'can_user_delete':obj.user == self.request.user,
        }

        vr = ValidateRoomView(room)
        if vr.is_room_exist():
            dict_queryset['can_user_delete'] = vr.is_admin(self.request.user)

        return dict_queryset

    def get_replies_after_order(self, replies):
        params = self.request.GET
        if ('order' not in params) or (params['order'] not in self.order.keys()):
            return replies

        for key in self.order.keys():
            self.order[key] = False
        self.order[params['order']] = True

        if params['order'] == 'favorite_count':
            return replies.order_by('-expansion__favorite_count')
        if params['order'] == 'reaction_count':
            return replies.annotate(reaction_count=F('expansion__agree_count')+F('expansion__disagree_count')).order_by('-reaction_count')
            
        return replies

class ShowRoomBaseView(HeaderView):
    def validate_room(self):
        self.vr = ValidateRoomView(get_dict_item(self.kwargs, 'room_pk'))
        if not self.vr.is_room_exist():
            raise Http404
        if not self.vr.is_public() and not self.vr.is_room_user(self.request.user):
            raise PermissionError
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

        context['video_path'] = get_img_path(room.video)
        context['img_paths'] = self.room_base.get_room_img_paths()
        context['tab_contents'] = json.dumps(self.room_base.get_tab_contents())
        context['tab_content1_items'] = json.dumps(self.room_base.get_tab_content_items(self.room.tabpermutation.tab_content1))
        context['dumps_request_information'] = json.dumps(self.room_base.get_room_request_information())

        context['do_pass_request_information'] = True
        if not self.vr.is_admin(self.request.user) and\
            self.vr.is_room_user(self.request.user) and\
                not RoomInformation.objects.filter(rri__room=room, user=self.request.user, is_deleted=False).exists():
            context['do_pass_request_information'] = True
        
        profile = room.admin.profile
        context['admin_img'] = get_img_path(profile.img)
        context['username'] = profile.user.username
        context['profession'] = profile.profession
        context['description'] = profile.description

        if not self.request.user.is_authenticated:
            return context

        if self.vr.is_admin(self.request.user):
            context['is_admin'] = True
            return context

        #todo (中) 基本的にobjects.filterは共通で書くようにする
        room_user = RoomUser.objects.filter(room=room, user=self.request.user, is_deleted=False)
        if room_user.exists():
            if room_user[0].is_blocked:
                context['is_blocked'] = True
            else:
                context['is_room_user'] = True
        else:
            room_guest = RoomGuest.objects.filter(room=room, guest=self.request.user, is_deleted=False)
            if room_guest.exists():
                context['is_waiting'] = True
        
        return context

class SendMailView(TemplateView):
    user_from = settings.EMAIL_HOST_USER 
    def send_mail(self, title, message, user_to):
        send_mail(
            title,
            message,
            self.user_from,
            user_to,
            fail_silently=False, 
        )

    def validate_email(self, email):
        try:
            validate_email(email)
        except:
            return False

        return not is_empty(email)

class DeleteBaseView(TemplateView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def validate_delete(self, room, user):
        vr = ValidateRoomView(room)
        if (vr.is_room_exist() and not vr.is_admin(self.request.user)) or self.request.user != user:
            raise MyBadRequest('no permission to delete.')