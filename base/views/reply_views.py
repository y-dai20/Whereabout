from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse, Http404

from base.forms import ReplyReplyForm, ReplyPostForm
from base.models.general_models import ObjectExpansion
from base.models.post_models import Post, PostAgree
from base.models.room_models import RoomReplyType
from base.models.reply_models import ReplyPost, ReplyReply, ReplyAgree, ReplyFavorite, ReplyDemagogy, Reply2Agree, Reply2Favorite, Reply2Demagogy
from base.views.general_views import AgreeView, FavoriteView, DetailBaseView, DemagogyView, SearchBaseView, IndexBaseView, RoomBase
from base.views.validate_views import ValidateRoomView
from base.views.functions import get_form_error_message, get_dict_item, is_empty, get_json_message, is_str, \
    get_file_size_by_unit, get_img_list, get_file_size, get_json_error
from base.views.mixins import LoginRequiredMixin

#todo AgreeやDisagreeを定数にしたい
class ReplyPostView(LoginRequiredMixin, CreateView):
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
        result = vr.validate_reply(request.user)
        if not result['is_success']:
            return JsonResponse(result)

        form = self.form_class(request.POST)
        if not form.is_valid():
            return get_json_message(False, 'エラー', get_form_error_message(form))

        room_base = RoomBase(vr.get_room())
        reply = form.save(commit=False)
        if reply.type not in room_base.get_room_reply_types():
            return get_json_error(500)

        img_list = get_img_list(request.POST, files, self.max_img)
        if get_file_size(img_list) > self.max_img_size:
            return JsonResponse(get_json_message(False, 'エラー', ['画像サイズが{}を超えています'.format(get_file_size_by_unit(self.max_img_size, unit='MB'))]))
        reply.img = img_list[0]
            
        reply.user = request.user
        reply.post = post
        reply.expansion = ObjectExpansion.objects.create()

        agree_post = PostAgree.objects.filter(obj=get_dict_item(kwargs, 'post_pk'), user=request.user, is_deleted=False)
        if agree_post.exists():
            reply.position = 'Agree' if agree_post[0].is_agree else 'Disagree'
        
        reply.save()
        post.expansion.reply_count += 1
        post.expansion.save()

        return JsonResponse(get_json_message(True,'成功',['返信しました']))

class ReplyReplyView(LoginRequiredMixin, CreateView):
    form_class = ReplyReplyForm
    template_name = 'pages/reply_detail.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        reply_post = get_object_or_404(ReplyPost, id=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)

        vr = ValidateRoomView(reply_post.post.room)
        result = vr.validate_reply(request.user)
        if not result['is_success']:
            return JsonResponse(result)
            
        form = self.form_class(request.POST)
        if not form.is_valid():
            return get_json_message(False, 'エラー', get_form_error_message(form))

        reply = form.save(commit=False)
        reply.user = request.user
        reply.reply = reply_post
        reply.expansion = ObjectExpansion.objects.create()
        reply.save()

        reply_post.expansion.reply_count += 1
        reply_post.expansion.save()

        return JsonResponse(get_json_message(True,'成功',['返信しました']))

class ReplyDetailView(DetailBaseView, SearchBaseView):
    template_name = 'pages/reply_detail.html'
    model = ReplyPost

    def get(self, request, *args, **kwargs):
        self.reply = get_object_or_404(ReplyPost, id=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        self.room = self.reply.post.room

        if not self.check_can_access(self.room):
            raise PermissionError()
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_post_detail_item(self.reply)
        return context

    def get_queryset(self):
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
            return self.get_reply_detail_items(self.get_items(replies2))

        agree_reply = self.get_replies_after_order(replies.filter(position='Agree'))
        len_ar = len(agree_reply)
        neutral_reply = self.get_replies_after_order(replies.filter(position='Neutral'))
        len_nr = len(neutral_reply)
        disagree_reply = self.get_replies_after_order(replies.filter(position='Disagree'))
        len_dr = len(disagree_reply)

        for idx in range(self.get_start_idx(), self.get_end_idx(max(len_ar, len_nr, len_dr))):
            queryset.append(self.get_reply_detail_item(agree_reply[idx]) if idx < len_ar else None)
            queryset.append(self.get_reply_detail_item(neutral_reply[idx]) if idx < len_nr else None)
            queryset.append(self.get_reply_detail_item(disagree_reply[idx]) if idx < len_dr else None)

        return queryset

class ReplyDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/index.html'
    model = ReplyPost

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        reply = get_object_or_404(self.model, pk=get_dict_item(kwargs, 'reply_pk'), is_deleted=False)
        vr = ValidateRoomView(reply.post.room)
        if (vr.is_room_exist() and not vr.is_admin(request.user)) or request.user != reply.user:
            return JsonResponse(get_json_message(False, 'エラー', ['削除に失敗しました']))

        reply.is_deleted = True
        reply.save()

        return JsonResponse(get_json_message(True,'成功',['削除しました']))

class Reply2DeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/index.html'
    model = ReplyReply

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        reply2 = get_object_or_404(self.model, pk=get_dict_item(kwargs, 'reply2_pk'), is_deleted=False)
        vr = ValidateRoomView(reply2.reply.post.room)
        if (vr.is_room_exist() and not vr.is_admin(request.user)) and request.user != reply2.user:
            return JsonResponse(get_json_message(False, 'エラー', ['削除に失敗しました']))

        reply2.is_deleted = True
        reply2.save()

        return JsonResponse(get_json_message(True,'成功',['削除しました']))

class ReplyAgreeView(AgreeView):
    model = ReplyAgree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)

        return JsonResponse(json_data)

class Reply2AgreeView(AgreeView):
    model = Reply2Agree
    template_name = 'pages/index.html'
    
    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)

        return JsonResponse(json_data)

class ReplyFavoriteView(FavoriteView):
    model = ReplyFavorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2FavoriteView(FavoriteView):
    model = Reply2Favorite
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class ReplyDemagogyView(DemagogyView):
    model = ReplyDemagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyPost, pk=get_dict_item(kwargs, 'reply_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.post.room)
        
        return JsonResponse(json_data)

class Reply2DemagogyView(DemagogyView):
    model = Reply2Demagogy
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        reply = get_object_or_404(ReplyReply, pk=get_dict_item(kwargs, 'reply2_pk'))
        json_data = self.get_json_data(obj=reply, room=reply.reply.post.room)
        
        return JsonResponse(json_data)

class GetReplyView(DetailBaseView, IndexBaseView):
    load_by = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        post = get_dict_item(self.request.POST, 'obj_id')
        if not is_str(post):
            return []

        replies = ReplyPost.objects.filter(post=post, is_deleted=False)
        return self.get_post_detail_items(self.get_idx_items(replies))

class GetReply2View(DetailBaseView, IndexBaseView):
    load_by = 1

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_items(self):
        reply = get_dict_item(self.request.POST, 'obj_id')
        if not is_str(reply):
            return []

        replies = ReplyReply.objects.filter(reply=reply, is_deleted=False)
        return self.get_reply_detail_items(self.get_idx_items(replies))