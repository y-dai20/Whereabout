from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect

import base.views.functions as f
from base.views.validate_views import ValidateRoomView

from functools import wraps

def login_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_active:
            if request.is_ajax():
                return JsonResponse(f.get_json_error_message(['ログインが必要です']))
            else:
                return redirect(settings.LOGIN_URL)
        return view(request, *args, **kwargs)
    return inner

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwds):
        return login_required(super().as_view(**kwds))

def room_admin_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.is_admin(request.user):
            if request.is_ajax():
                return JsonResponse(f.get_json_error_message(['不正なアクセスです']))
            else:
                return redirect('/error/')
        return view(request, *args, **kwargs)
    return inner

class RoomAdminRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwds):
        return room_admin_required(super().as_view(**kwds))

def room_access_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        vr = ValidateRoomView(f.get_dict_item(kwargs, 'room_pk'))
        if not vr.can_access(request.user):
            if request.is_ajax():
                return JsonResponse(f.get_json_error_message(['不正なアクセスです']))
            else:
                return redirect('/error/')
        return view(request, *args, **kwargs)
    return inner

class RoomAccessRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwds):
        return room_access_required(super().as_view(**kwds))
