from django.views.generic import DetailView
from django.http import JsonResponse, Http404


import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.models import UserFollow, User, UserBlock
from base.models.room_models import RoomUser
from base.views.mixins import LoginRequiredMixin

class FollowView(LoginRequiredMixin, DetailView):
    model = UserFollow
    template_name = 'pages/user.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        target_user = f.get_object_or_404_from_q(User.objects.active(username=f.get_dict_item(self.kwargs, 'username')))
        if request.user.username == target_user.username:
            return JsonResponse(f.get_json_error_message(['自身をフォローできません']))

        if UserBlock.objects.active(blocker=request.user, blockee=target_user).exists():
            raise MyBadRequest('user is blocked.')
        
        follow = UserFollow.objects.get_or_none(follower=request.user, followee=target_user)
        if follow is None:
            follow.create(follower=request.user, followee=target_user)
        else:
            follow.is_deleted = not follow.is_deleted
            follow.save()
        
        profile = target_user.profile
        profile.followed_count = UserFollow.objects.active(followee=target_user).count()
        profile.save()

        return JsonResponse(f.get_json_success_message(add_dict={'is_follow':not follow.is_deleted}))

class BlockView(LoginRequiredMixin, DetailView):
    model = UserBlock
    template_name = 'pages/user.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        target_user = f.get_object_or_404_from_q(User.objects.active(username=f.get_dict_item(self.kwargs, 'username')))
        if request.user.username == target_user.username:
            return JsonResponse(f.get_json_error_message(['自身をブロックできません']))

        block = UserBlock.objects.get_or_none(blocker=request.user, blockee=target_user)
        if block is None:
            block.create(blocker=request.user, blockee=target_user)
        else:
            block.is_deleted = not block.is_deleted
            block.save()

        if not block.is_deleted:
            UserFollow.objects.active(follower=request.user, followee=target_user).update(is_deleted=True)
            RoomUser.objects.filter(room__admin=request.user, user=target_user).update(is_blocked=True)
        
        profile = target_user.profile
        profile.followed_count = UserFollow.objects.active(followee=target_user).count()
        profile.blocked_count = UserBlock.objects.active(blockee=target_user).count()
        profile.save()

        return JsonResponse(f.get_json_success_message(add_dict={
            'is_block':not block.is_deleted,
            'followed_count':f.get_number_unit(profile.followed_count),
            'blocked_count':f.get_number_unit(profile.blocked_count),
        }))