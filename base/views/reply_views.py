from django.views.generic import CreateView
from django.http import JsonResponse, Http404
from django.db.models import F


import base.views.functions as f
from base.views.exceptions import MyBadRequest
from base.forms import ReplyReplyForm, ReplyPostForm
from base.models.post_models import Post, PostAgree
from base.models.reply_models import ReplyPost, ReplyReply, ReplyAgree, ReplyFavorite, ReplyDemagogy, Reply2Agree, Reply2Favorite, Reply2Demagogy, ReplyPosition
from base.views.general_views import AgreeView, FavoriteView, DetailBaseView, DemagogyView, SearchBaseView, IndexBaseView,\
    RoomBase, DeleteBaseView, ReplyItemView, Reply2ItemView
from base.views.validate_views import ValidateRoomView
from base.views.mixins import LoginRequiredMixin

import json

class ReplyPostView(LoginRequiredMixin, ReplyItemView, CreateView):
    form_class = ReplyPostForm
    template_name = 'pages/post_detail.html'
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        post = f.get_object_or_404_from_q(Post.objects.active(id=f.get_dict_item(kwargs, 'post_pk')))
        files = request.FILES

        vr = ValidateRoomView(post.room)
        if not vr.validate_reply(request.user):
            return JsonResponse(f.get_json_error_message(vr.get_error_messages()))

        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        room_base = RoomBase(vr.get_room())
        reply = form.save(commit=False)
        if reply.type not in room_base.get_room_reply_types():
            raise MyBadRequest('reply_type is not exist.')

        img_list = f.get_img_list(request.POST, files, self.max_img)
        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        reply.img = img_list[0]
            
        reply.user = request.user
        reply.post = post

        agree_post = PostAgree.objects.active(obj=f.get_dict_item(kwargs, 'post_pk'), user=request.user)
        if agree_post.exists():
            reply.position = ReplyPosition.AGREE if agree_post[0].is_agree else ReplyPosition.DISAGREE

        reply.save()
        post.reply_count += 1
        post.save()

        return JsonResponse(f.get_json_success_message(['返信しました'], {'reply':self.get_reply_item(reply)}))

class ReplyReplyView(LoginRequiredMixin, Reply2ItemView, CreateView):
    form_class = ReplyReplyForm
    template_name = 'pages/reply_detail.html'
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyPost.objects.active(id=f.get_dict_item(kwargs, 'reply_pk')))
        files = request.FILES

        vr = ValidateRoomView(reply.post.room)
        if not vr.validate_reply(request.user):
            return JsonResponse(f.get_json_error_message(vr.get_error_messages()))
            
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(f.get_json_error_message(f.get_form_error_message(form)))

        room_base = RoomBase(vr.get_room())
        reply2 = form.save(commit=False)
        if reply2.type not in room_base.get_room_reply_types():
            raise MyBadRequest('reply_type is not exist.')

        img_list = f.get_img_list(request.POST, files, self.max_img)
        if f.get_file_size(img_list) > self.max_img_size:
            return JsonResponse(f.get_json_error_message(['画像サイズが{}を超えています'.format(f.get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        reply2.img = img_list[0]
        
        reply2.user = request.user
        reply2.reply = reply
        reply2.save()

        reply.reply_count += 1
        reply.save()

        return JsonResponse(f.get_json_success_message(['返信しました'], {'reply':self.get_reply2_item(reply2)}))

class ReplyDetailView(ReplyItemView, Reply2ItemView, DetailBaseView):
    template_name = 'pages/reply_detail.html'
    model = ReplyPost

    def get(self, request, *args, **kwargs):
        self.reply = f.get_object_or_404_from_q(ReplyPost.objects.active(id=f.get_dict_item(kwargs, 'reply_pk')))
        self.check_can_access(self.reply.post.room)
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_reply_item(self.reply)
        context['dumps_reply'] = json.dumps(obj)
        context['obj_id'] = obj['obj_id']
        room_base = RoomBase(obj['obj_id'])
        context['reply_types'] = room_base.get_room_reply_types()

        return context

    def get_items(self):
        params = self.get_params()
        replies = ReplyReply.objects.active(
            reply=f.get_dict_item(self.kwargs, 'reply_pk'),
            user__username__icontains=params['username'],
            text__icontains=params['text'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            type__icontains=params['type'],
        )
        
        items = []
        if not f.is_empty(params['position']) and params['position'].upper() in ReplyPosition.names:
            replies2 = self.get_replies_after_order(replies.filter(position=ReplyPosition[params['position'].upper()]))
            self.load_by *= 3
            return self.get_reply2_items(self.get_idx_items(replies2))

        agree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.AGREE))
        len_ar = len(agree_reply)
        neutral_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.NEUTRAL))
        len_nr = len(neutral_reply)
        disagree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.DISAGREE))
        len_dr = len(disagree_reply)

        for idx in range(self.get_start_idx(), self.get_end_idx(max(len_ar, len_nr, len_dr))):
            items.append(self.get_reply2_item(agree_reply[idx]) if idx < len_ar else None)
            items.append(self.get_reply2_item(neutral_reply[idx]) if idx < len_nr else None)
            items.append(self.get_reply2_item(disagree_reply[idx]) if idx < len_dr else None)

        return items

class ReplyDeleteView(LoginRequiredMixin, DeleteBaseView):
    model = ReplyPost

    def post(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(self.model.objects.active(pk=f.get_dict_item(kwargs, 'reply_pk')))
        self.validate_delete(reply.post.room, reply.user)
        reply.is_deleted = True
        reply.save()

        return JsonResponse(f.get_json_success_message(['削除しました']))

class Reply2DeleteView(LoginRequiredMixin, DeleteBaseView):
    model = ReplyReply

    def post(self, request, *args, **kwargs):
        reply2 = f.get_object_or_404_from_q(self.model.objects.active(pk=f.get_dict_item(kwargs, 'reply2_pk')))
        self.validate_delete(reply2.reply.post.room, reply2.user)
        reply2.is_deleted = True
        reply2.save()

        return JsonResponse(f.get_json_success_message(['削除しました']))

class ReplyAgreeView(AgreeView):
    model = ReplyAgree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyPost.objects.active(pk=f.get_dict_item(kwargs, 'reply_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)

        return JsonResponse(json_data)

class Reply2AgreeView(AgreeView):
    model = Reply2Agree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyReply.objects.active(pk=f.get_dict_item(kwargs, 'reply2_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)

        return JsonResponse(json_data)

class ReplyFavoriteView(FavoriteView):
    model = ReplyFavorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyPost.objects.active(pk=f.get_dict_item(kwargs, 'reply_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2FavoriteView(FavoriteView):
    model = Reply2Favorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyReply.objects.active(pk=f.get_dict_item(kwargs, 'reply2_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class ReplyDemagogyView(DemagogyView):
    model = ReplyDemagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyPost.objects.active(pk=f.get_dict_item(kwargs, 'reply_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2DemagogyView(DemagogyView):
    model = Reply2Demagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = f.get_object_or_404_from_q(ReplyReply.objects.active(pk=f.get_dict_item(kwargs, 'reply2_pk')))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class GetReplyView(ReplyItemView, IndexBaseView):
    load_by = 10

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        post = f.get_object_or_404_from_q(Post.objects.active(id=f.get_dict_item(self.request.POST, 'obj_id')))
        self.check_can_access(post.room)
        replies = ReplyPost.objects.active(post=post)
        replies = replies.annotate(reaction_count=F('agree_count')+F('disagree_count')).order_by('-reaction_count')
        return self.get_reply_items(self.get_idx_items(replies))

class GetReply2View(Reply2ItemView, IndexBaseView):
    load_by = 10

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        reply = f.get_object_or_404_from_q(ReplyPost.objects.active(id=f.get_dict_item(self.request.POST, 'obj_id')))
        self.check_can_access(reply.post.room)
        replies = ReplyReply.objects.active(reply=reply)
        replies = replies.annotate(reaction_count=F('agree_count')+F('disagree_count')).order_by('-reaction_count')
        return self.get_reply2_items(self.get_idx_items(replies))