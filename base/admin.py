from base.forms import SignUpForm
from django.contrib import admin
from base.models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        (None, {'fields': ('is_active', 'is_admin',)}),
    )
 
    list_display = ('username', 'email', 'is_active',)
    list_filter = ()
    ordering = ()
    filter_horizontal = ()
 
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password','is_active',)}),
    )
 
    add_form = SignUpForm
 
 
admin.site.register(User, CustomUserAdmin)
admin.site.register(Guest)
admin.site.register(UserReset)
admin.site.register(Profile)
admin.site.register(UserEvaluate)
admin.site.register(UserFollow)
admin.site.register(UserBlock)

admin.site.register(Post)
admin.site.register(PostImgs)
admin.site.register(PostAgree)
admin.site.register(PostFavorite)
admin.site.register(PostDemagogy)

admin.site.register(ReplyPost)
admin.site.register(ReplyReply)
admin.site.register(ReplyAgree)
admin.site.register(ReplyFavorite)
admin.site.register(ReplyDemagogy)

admin.site.register(RoomAuthority)
admin.site.register(Room)
admin.site.register(RoomImgs)
admin.site.register(TabPermutation)
admin.site.register(TabContent)
admin.site.register(TabContentItem)
admin.site.register(RoomReplyType)
admin.site.register(RoomGuest)
admin.site.register(RoomUser)
admin.site.register(RoomInviteUser)
admin.site.register(RoomGood)
admin.site.register(RoomRequestInformation)
admin.site.register(RoomInformation)

admin.site.register(ObjectExpansion)