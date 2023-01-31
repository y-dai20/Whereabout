from django.db.models import Q


import base.views.functions as f
from base.models.post_models import Post, PostFavorite
from base.models.room_models import Room
from base.models.account_models import Profile, User
from base.views.general_views import PostItemView, RoomItemView, UserItemView, SearchBaseView, RoomBase

class IndexPostListView(SearchBaseView, PostItemView):
    template_name = 'pages/index.html'
    model = Post
    load_by = 2
    checked_label = 'on'

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
            # 'agree-state':'', 
            # 'true-state':''
        }

    def get_items(self):
        if f.is_empty(dict(self.request.GET)):
            if self.request.user.is_authenticated:
                self.search['my_room_check'] = self.checked_label
            else:
                self.search['no_room_check'] = self.checked_label

        params = self.get_params()
        posts = Post.objects.filter(
            is_deleted=False, 
            user__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
        ).exclude(user__id__in=self.get_blocked_user_list())
        
        if params['is_favorite'] and self.request.user.is_authenticated:
            fav_ids = PostFavorite.objects.filter(user=self.request.user, is_deleted=False).values_list('obj__id', flat=True)
            posts = posts.filter(id__in=fav_ids)

        my_rooms = RoomBase.get_my_room_list(self.request.user)
        attend_rooms = RoomBase.get_attend_room_list(self.request.user)
        rooms = my_rooms if self.checked_label == self.search['my_room_check'] else []
        rooms += attend_rooms if self.checked_label == self.search['attend_room_check'] else []
        rooms += RoomBase.get_other_room_list(my_rooms + attend_rooms) if self.checked_label == self.search['other_room_check'] else []

        if self.checked_label == self.search['no_room_check']:
            posts = posts.filter(Q(room__in=rooms) | Q(room__isnull=True))
        else:
            posts = posts.filter(room__in=rooms)

        return self.get_post_items(self.get_idx_items(posts))

class IndexRoomListView(SearchBaseView, RoomItemView):
    template_name = 'pages/index_room.html'
    model = Room
    load_by = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'', 
            'title':'', 
            'date_from':'', 
            'date_to':'',
            'participant_from':'',
            'participant_to':'',
        }

    def get_items(self):
        params = self.get_params()
        rooms = Room.objects.filter(
            is_deleted=False, 
            is_public=True,
            admin__username__icontains=params['username'],
            title__icontains=params['title'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            participant_count__gte=params['participant_from'] if f.is_int(params['participant_from']) else 0,
        ).exclude(admin__id__in=self.get_blocked_user_list())

        if f.is_int(params['participant_to']):
            rooms = rooms.filter(participant_count__lte=params['participant_to'])
        
        return self.get_room_items(self.get_idx_items(rooms))

class IndexUserListView(SearchBaseView, UserItemView):
    template_name = 'pages/index_user.html'
    model = User
    load_by = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = {
            'username':'', 
            'profession':'', 
            'description':'', 
            'date_from':'', 
            'date_to':'',
            'is_blocked':''
        }

    def get_items(self):
        params = self.get_params()
        profile = Profile.objects.filter(
            is_deleted=False,
            user__is_active=True,
            user__username__icontains=params['username'],
            profession__icontains=params['profession'], 
            description__icontains=params['description'], 
            user__created_at__gte=params['date_from'], 
            user__created_at__lte=params['date_to'],
        )

        if f.get_boolean_or_none(params['is_blocked']) == True:
            profile = profile.filter(user__id__in=self.get_blocked_user_list())
        else:
            profile = profile.exclude(user__id__in=self.get_blocked_user_list())
        
        return self.get_user_items(self.get_idx_items(profile))
