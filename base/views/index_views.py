from django.db.models import Q, Value as V
import django.db.models.functions as mf
from django.db.models import F, DateTimeField

import base.views.functions as f
from base.models.post_models import Post, PostFavorite
from base.models.room_models import Room
from base.models.account_models import Profile, User
from base.views.general_views import PostItemView, RoomItemView, UserItemView, SearchBaseView, RoomBase

class IndexPostListView(SearchBaseView, PostItemView):
    template_name = 'pages/index.html'
    model = Post
    load_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'', 
            'title':'', 
            'date_from':'', 
            'date_to':'', 
            'my_room_check':'', 
            'attend_room_check':'', 
            'other_room_check':'', 
            'no_room_check':'', 
            'is_favorite':'',
            'tags':'',
            # 'agree-state':'', 
            # 'true-state':''
        }
        self.order = {
            'ranking':True,
            'created_at':False,
            'favorite_count':False,
        }

    def get_items(self):
        if f.is_empty(dict(self.request.GET)):
            if self.request.user.is_authenticated:
                self.search['my_room_check'] = True
            else:
                self.search['no_room_check'] = True

        params = self.get_params()
        posts = Post.objects.active(
            user__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
        ).exclude(user__id__in=self.get_blocked_user_list())
        
        if params['is_favorite'] and self.request.user.is_authenticated:
            fav_ids = PostFavorite.objects.active(user=self.request.user).values_list('obj__id', flat=True)
            posts = posts.filter(id__in=fav_ids)

        my_rooms = RoomBase.get_my_room_list(self.request.user)
        attend_rooms = RoomBase.get_attend_room_list(self.request.user)
        rooms = my_rooms if params['my_room_check'] == True else []
        rooms += attend_rooms if params['attend_room_check'] == True else []
        rooms += RoomBase.get_other_room_list(my_rooms + attend_rooms) if params['other_room_check'] == True else []

        if params['no_room_check'] == True:
            posts = posts.filter(Q(room__in=rooms) | Q(room__isnull=True))
        else:
            posts = posts.filter(room__in=rooms)

        if not f.is_empty(params['tags']):
            posts = posts.annotate(
                tags=mf.Concat(V('&'), 'tag_sequence__tag1__name', 
                            V('&'), 'tag_sequence__tag2__name', 
                            V('&'), 'tag_sequence__tag3__name', 
                            V('&'), 'tag_sequence__tag4__name', 
                            V('&'), 'tag_sequence__tag5__name', V('&')))
            for tag in params['tags'].split(','):
                posts = posts.filter(tags__contains='&{}&'.format(tag))

        order = self.get_order()
        if order['ranking']:
            posts = posts.annotate(rank=F('agree_count') - F('disagree_count')).order_by('-rank')
        elif order['favorite_count']:
            posts = posts.order_by('-favorite_count')

        return self.get_post_items(self.get_idx_items(posts))

#todo (中) デフォルトの並びを急上昇などにしたい
class IndexRoomListView(SearchBaseView, RoomItemView):
    template_name = 'pages/index_room.html'
    model = Room
    load_by = 15

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'', 
            'title':'', 
            'date_from':'', 
            'date_to':'',
            'participant_from':'',
            'participant_to':'',
            'tags':'',
        }
    #todo (中) タグ検索の追加
    def get_items(self):
        params = self.get_params()
        rooms = Room.objects.active(
            admin__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            participant_count__gte=params['participant_from'] if f.is_int(params['participant_from']) else 0,
        ).public().exclude(admin__id__in=self.get_blocked_user_list())

        if f.is_int(params['participant_to']):
            rooms = rooms.filter(participant_count__lte=params['participant_to'])

        if not f.is_empty(params['tags']):
            rooms = rooms.annotate(
                tags=mf.Concat(V('&'), 'tag_sequence__tag1__name', 
                            V('&'), 'tag_sequence__tag2__name', 
                            V('&'), 'tag_sequence__tag3__name', 
                            V('&'), 'tag_sequence__tag4__name', 
                            V('&'), 'tag_sequence__tag5__name', 
                            V('&'), 'tag_sequence__tag6__name', 
                            V('&'), 'tag_sequence__tag7__name', 
                            V('&'), 'tag_sequence__tag8__name', 
                            V('&'), 'tag_sequence__tag9__name', 
                            V('&'), 'tag_sequence__tag10__name', V('&')))
            for tag in params['tags'].split(','):
                rooms = rooms.filter(tags__contains='&{}&'.format(tag))
        
        # rooms = rooms.annotate(diff_now=mf.Cast(mf.Now() - F('created_at'), output_field=DateTimeField())).annotate(
        #     rank=mf.Round((mf.ExtractYear('diff_now')*365+mf.ExtractMonth('diff_now')*30+mf.ExtractDay('diff_now'))/(F('good_count')+F('bad_count')*0.5+F('participant_count')*1.5))
        # ).order_by('rank')
        # print(rooms[0].rank)
        return self.get_room_items(self.get_idx_items(rooms))

class IndexUserListView(SearchBaseView, UserItemView):
    template_name = 'pages/index_user.html'
    model = User
    load_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'', 
            'profession':'', 
            'description':'', 
            'date_from':'', 
            'date_to':'',
            'is_blocked':'',
            'tags':'',
        }

    def get_items(self):
        params = self.get_params()
        profiles = Profile.objects.active(
            user__username__icontains=params['username'],
            profession__icontains=params['profession'], 
            description__icontains=params['description'], 
            user__created_at__gte=params['date_from'], 
            user__created_at__lte=params['date_to'],
        )

        if f.get_boolean_or_none(params['is_blocked']) == True:
            profiles = profiles.filter(user__id__in=self.get_blocked_user_list())
        else:
            profiles = profiles.exclude(user__id__in=self.get_blocked_user_list())

        if not f.is_empty(params['tags']):
            profiles = profiles.annotate(
                tags=mf.Concat(V('&'), 'tag_sequence__tag1__name', 
                            V('&'), 'tag_sequence__tag2__name', 
                            V('&'), 'tag_sequence__tag3__name', 
                            V('&'), 'tag_sequence__tag4__name', 
                            V('&'), 'tag_sequence__tag5__name', V('&')))
            for tag in params['tags'].split(','):
                profiles = profiles.filter(tags__contains='&{}&'.format(tag))
        
        return self.get_user_items(self.get_idx_items(profiles))
