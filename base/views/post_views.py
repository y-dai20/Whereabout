from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse, Http404


from base.views.exceptions import MyBadRequest
from base.models.general_models import ObjectExpansion
from base.models.reply_models import ReplyPost, ReplyPosition
from base.models.post_models import Post, PostAgree, PostFavorite, PostImgs
from base.forms import PostForm
from base.views.functions import get_form_error_message, get_file_size_by_unit, get_dict_item, is_empty,\
    get_img_list, get_file_size, get_video_list, get_json_success_message, get_json_error_message
from base.views.general_views import SearchBaseView, DemagogyView, AgreeView, FavoriteView, DetailBaseView, PostItemView, PostDemagogy, RoomBase, DeleteBaseView
from base.views.validate_views import ValidateRoomView
from base.views.mixins import LoginRequiredMixin

import json

class PostView(LoginRequiredMixin, PostItemView, CreateView):
    form_class = PostForm
    template_name = 'pages/index.html'
    max_img = 4
    max_video = 1
    max_img_size = 2 * 1024 * 1024
    max_video_size = 11 * 1024 * 1024

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        vr = ValidateRoomView(get_dict_item(request.POST, 'room_id'))

        if not vr.validate_post(request.user):
            return JsonResponse(get_json_error_message(vr.get_error_messages()))

        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(get_json_error_message(get_form_error_message(form)))

        post = form.save(commit=False)
        post.user = request.user
        post.room = vr.get_room()
        post.expansion = ObjectExpansion.objects.create()

        files = request.FILES
        video_list = get_video_list(request.POST, files, self.max_video)
        if get_file_size(video_list) > self.max_video_size:
                return JsonResponse(get_json_error_message(['動画サイズが{}を超えています'.format(get_file_size_by_unit(self.max_video_size, unit='MB'))]))
        post.video = video_list[0]
        
        img_list = get_img_list(request.POST, files, self.max_img)
        if get_file_size(img_list) > self.max_img_size:
            return JsonResponse(get_json_error_message(['画像サイズが{}を超えています'.format(get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        
        if get_file_size(video_list) > 0 and get_file_size(img_list) > 0:
            raise MyBadRequest('only img or video.')

        post.save()
        PostImgs.objects.create(
            post=post,
            img1 = img_list[0],
            img2 = img_list[1],
            img3 = img_list[2],
            img4 = img_list[3],
        )

        return JsonResponse(get_json_success_message(['投稿しました'], {'post':self.get_post_item(post)}))

class PostDetailView(DetailBaseView, SearchBaseView):
    model = ReplyPost
    template_name = 'pages/post_detail.html'
        
    def get(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, id=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        self.check_can_access(self.post.room)

        return super().get(request, *args, **kwargs)

    def get_items(self):
        params = self.get_params()
        replies = ReplyPost.objects.filter(
            post=get_dict_item(self.kwargs, 'post_pk'),
            user__username__icontains=params['username'],
            text__icontains=params['text'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            type__icontains=params['type'],
            is_deleted=False,
        )

        if not is_empty(params['position']):
            #todo (中) search_reply.htmlと密結合になっている．Agreeなどが送られてこないと検索に引っかからない
            post_replies = self.get_replies_after_order(replies.filter(position=params['position']))
            self.load_by *= 3
            return self.get_post_detail_items(self.get_idx_items(post_replies))

        agree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.AGREE))
        len_ar = len(agree_reply)
        neutral_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.NEUTRAL))
        len_nr = len(neutral_reply)
        disagree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.DISAGREE))
        len_dr = len(disagree_reply)

        items = []
        for idx in range(self.get_start_idx(), self.get_end_idx(max(len_ar, len_nr, len_dr))):
            items.append(self.get_post_detail_item(agree_reply[idx]) if idx < len_ar else None)
            items.append(self.get_post_detail_item(neutral_reply[idx]) if idx < len_nr else None)
            items.append(self.get_post_detail_item(disagree_reply[idx]) if idx < len_dr else None)

        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_post_item(self.post)
        context['dumps_post'] = json.dumps(obj)
        context['obj_id'] = obj['obj_id']
        room_base = RoomBase(obj['room_id'])
        context['reply_types'] = room_base.get_room_reply_types()

        return context

# class PostEditView(LoginRequiredMixin, UpdateView):
#     model = Post
#     template_name = 'pages/post_item.html'
#     form_class = PostForm
    
#     def get_success_url(self):
#         return reverse("post_detail", kwargs={"pk":self.object.pk})

#     def post(self, request, *args, **kwargs):
#         post = get_object_or_404(Post, pk=kwargs['post_pk'])
#         if request.user != post.user:
#             return redirect(request.META['HTTP_REFERER'])

#         return super().post(request, *args, **kwargs)

class PostDeleteView(LoginRequiredMixin, DeleteBaseView):
    model = Post

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        self.validate_delete(post.room, post.user)
        post.is_deleted = True
        post.save()

        return JsonResponse(get_json_success_message(['削除しました']))

class PostAgreeView(AgreeView):
    model = PostAgree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=post, room=post.room)

        return JsonResponse(json_data)

class PostFavoriteView(FavoriteView):
    model = PostFavorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=post, room=post.room)
        
        return JsonResponse(json_data)

class PostDemagogyView(DemagogyView):
    model = PostDemagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=post, room=post.room)
        
        return JsonResponse(json_data)

class GetPostReplyTypesView(TemplateView):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        room_base = RoomBase(post.room)
        return JsonResponse(get_json_success_message(add_dict={'reply_types':room_base.get_room_reply_types()}))

class GetReplyReplyTypesView(TemplateView):
    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, id=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        room_base = RoomBase(reply.post.room)
        return JsonResponse(get_json_success_message(add_dict={'reply_types':room_base.get_room_reply_types()}))
