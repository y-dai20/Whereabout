from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse, Http404


from base.views.exceptions import MyBadRequest
from base.forms import ReplyReplyForm, ReplyPostForm
from base.models.general_models import ObjectExpansion
from base.models.post_models import Post, PostAgree
from base.models.room_models import RoomReplyType
from base.models.reply_models import ReplyPost, ReplyReply, ReplyAgree, ReplyFavorite, ReplyDemagogy, Reply2Agree, Reply2Favorite, Reply2Demagogy, ReplyPosition
from base.views.general_views import AgreeView, FavoriteView, DetailBaseView, DemagogyView, SearchBaseView, IndexBaseView,\
    RoomBase, DeleteBaseView, ReplyItemView, Reply2ItemView
from base.views.validate_views import ValidateRoomView
from base.views.functions import get_form_error_message, get_dict_item, is_empty, is_str, \
    get_file_size_by_unit, get_img_list, get_file_size, get_json_error_message, get_json_success_message
from base.views.mixins import LoginRequiredMixin

class ReplyPostView(LoginRequiredMixin, ReplyItemView, CreateView):
    form_class = ReplyPostForm
    template_name = 'pages/post_detail.html'
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=get_dict_item(kwargs, 'post_pk'), is_deleted=False)
        files = request.FILES

        vr = ValidateRoomView(post.room)
        if not vr.validate_reply(request.user):
            return JsonResponse(get_json_error_message(vr.get_error_messages()))

        form = self.form_class(request.POST)
        if not form.is_valid():
            return get_json_error_message(get_form_error_message(form))

        room_base = RoomBase(vr.get_room())
        reply = form.save(commit=False)
        if reply.type not in room_base.get_room_reply_types():
            raise MyBadRequest('reply_type is not exist.')

        img_list = get_img_list(request.POST, files, self.max_img)
        if get_file_size(img_list) > self.max_img_size:
            return JsonResponse(get_json_error_message(['画像サイズが{}を超えています'.format(get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        reply.img = img_list[0]
            
        reply.user = request.user
        reply.post = post
        reply.expansion = ObjectExpansion.objects.create()

        agree_post = PostAgree.objects.filter(obj=get_dict_item(kwargs, 'post_pk'), user=request.user, is_deleted=False)
        if agree_post.exists():
            reply.position = ReplyPosition.AGREE if agree_post[0].is_agree else ReplyPosition.DISAGREE

        reply.save()
        post.expansion.reply_count += 1
        post.expansion.save()

        return JsonResponse(get_json_success_message(['返信しました'], {'reply':self.get_reply_item(reply)}))

class ReplyReplyView(LoginRequiredMixin, Reply2ItemView, CreateView):
    form_class = ReplyReplyForm
    template_name = 'pages/reply_detail.html'
    max_img_size = 2 * 1024 * 1024
    max_img = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, id=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        files = request.FILES

        vr = ValidateRoomView(reply.post.room)
        if not vr.validate_reply(request.user):
            return JsonResponse(get_json_error_message(vr.get_error_messages()))
            
        form = self.form_class(request.POST)
        if not form.is_valid():
            return get_json_error_message(get_form_error_message(form))

        room_base = RoomBase(vr.get_room())
        reply2 = form.save(commit=False)
        if reply2.type not in room_base.get_room_reply_types():
            raise MyBadRequest('reply_type is not exist.')

        img_list = get_img_list(request.POST, files, self.max_img)
        if get_file_size(img_list) > self.max_img_size:
            return JsonResponse(get_json_error_message(['画像サイズが{}を超えています'.format(get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        reply2.img = img_list[0]
        
        reply2.user = request.user
        reply2.reply = reply
        reply2.expansion = ObjectExpansion.objects.create()
        reply2.save()

        reply.expansion.reply_count += 1
        reply.expansion.save()

        return JsonResponse(get_json_success_message(['返信しました'], {'reply':self.get_reply2_item(reply2)}))

class ReplyDetailView(ReplyItemView, Reply2ItemView, DetailBaseView, SearchBaseView):
    template_name = 'pages/reply_detail.html'
    model = ReplyPost

    def get(self, request, *args, **kwargs):
        self.reply = get_object_or_404(ReplyPost, id=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        self.check_can_access(self.reply.post.room)
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_reply_item(self.reply)
        return context

    def get_items(self):
        params = self.get_params()
        replies = ReplyReply.objects.filter(
            reply=get_dict_item(self.kwargs, 'reply_pk'),
            user__username__icontains=params['username'],
            text__icontains=params['text'], 
            created_at__gte=params['date_from'], 
            created_at__lte=params['date_to'],
            type__icontains=params['type'],
            is_deleted=False,
        )
        
        queryset = []
        if not is_empty(params['position']):
            replies2 = self.get_replies_after_order(replies.filter(position=params['position']))
            self.load_by *= 3
            return self.get_reply2_items(self.get_idx_items(replies2))

        agree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.AGREE))
        len_ar = len(agree_reply)
        neutral_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.NEUTRAL))
        len_nr = len(neutral_reply)
        disagree_reply = self.get_replies_after_order(replies.filter(position=ReplyPosition.DISAGREE))
        len_dr = len(disagree_reply)

        for idx in range(self.get_start_idx(), self.get_end_idx(max(len_ar, len_nr, len_dr))):
            queryset.append(self.get_reply2_item(agree_reply[idx]) if idx < len_ar else None)
            queryset.append(self.get_reply2_item(neutral_reply[idx]) if idx < len_nr else None)
            queryset.append(self.get_reply2_item(disagree_reply[idx]) if idx < len_dr else None)

        return queryset

class ReplyDeleteView(LoginRequiredMixin, DeleteBaseView):
    model = ReplyPost

    def post(self, request, *args, **kwargs):
        reply = get_object_or_404(self.model, pk=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        self.validate_delete(reply.post.room, reply.user)
        reply.is_deleted = True
        reply.save()

        return JsonResponse(get_json_success_message(['削除しました']))

class Reply2DeleteView(LoginRequiredMixin, DeleteBaseView):
    model = ReplyReply

    def post(self, request, *args, **kwargs):
        reply2 = get_object_or_404(self.model, pk=get_dict_item(kwargs, 'reply2_pk'), is_deleted=False)
        self.validate_delete(reply2.reply.post.room, reply2.user)
        reply2.is_deleted = True
        reply2.save()

        return JsonResponse(get_json_success_message(['削除しました']))

class ReplyAgreeView(AgreeView):
    model = ReplyAgree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.post.room)

        return JsonResponse(json_data)

class Reply2AgreeView(AgreeView):
    model = Reply2Agree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)

        return JsonResponse(json_data)

class ReplyFavoriteView(FavoriteView):
    model = ReplyFavorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2FavoriteView(FavoriteView):
    model = Reply2Favorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class ReplyDemagogyView(DemagogyView):
    model = ReplyDemagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2DemagogyView(DemagogyView):
    model = Reply2Demagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'), is_deleted=False)
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class GetReplyView(ReplyItemView, IndexBaseView):
    load_by = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        post = get_object_or_404(Post, id=get_dict_item(self.request.POST, 'obj_id'), is_deleted=False)
        self.check_can_access(post.room)
        replies = ReplyPost.objects.filter(post=post, is_deleted=False)
        return self.get_reply_items(self.get_idx_items(replies))

class GetReply2View(Reply2ItemView, IndexBaseView):
    load_by = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        reply = get_object_or_404(ReplyPost, id=get_dict_item(self.request.POST, 'obj_id'), is_deleted=False)
        self.check_can_access(reply.post.room)
        replies = ReplyReply.objects.filter(reply=reply, is_deleted=False)
        return self.get_reply2_items(self.get_idx_items(replies))