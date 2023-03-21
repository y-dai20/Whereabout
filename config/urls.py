"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from .sitemaps import RoomSitemap, StaticSitemap

sitemaps = {
    'room':RoomSitemap,
    'static':StaticSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    # Get
    path('get/room-tab-items/', views.GetRoomTabItems.as_view(), name='get-room-tab-items'),
    path('get/reply/', views.GetReplyView.as_view(), name='get-reply'),
    path('get/reply2/', views.GetReply2View.as_view(), name='get-reply2'),
    path('get/tag/', views.GetTag.as_view(), name='get-tag'),
    path('get/reply-types/post/<str:post_pk>/', views.GetPostReplyTypesView.as_view(), name='get-post-reply-types'),
    path('get/reply-types/reply/<str:reply_pk>/', views.GetReplyReplyTypesView.as_view(), name='get-reply-reply-types'),
    path('get/user/<str:username>/', views.GetUserView.as_view(), name='get-user'),
    path('get/room/<str:room_pk>/', views.GetRoomView.as_view(), name='get-room'),
    path('get/room-request-information/<str:room_pk>/', views.GetRoomRequestInformationView.as_view(), name='get-room-request-information'),

    # Account
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.SendMailForSignupView.as_view(), name='send-mail-signup'),
    path('signup/<str:one_time_id>/', views.SignUpView.as_view(), name='signup'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', views.SendMailForResetPasswordView.as_view(), name='send-mail-reset-password'),
    path('reset-password/<str:one_time_id>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('modal/search/user/', views.ModalSearchUserView.as_view(), name='search-user'),

    # Room
    path('room/<str:room_pk>/', views.ShowRoomView.as_view(), name='room'),
    path('room/good/<str:room_pk>/', views.RoomGoodView.as_view(), name='room-good'),
    path('room/information/<str:room_pk>/', views.RoomInformationView.as_view(), name='room-information'),
    path('room/<str:room_pk>/<str:room_tab_pk>/', views.ShowRoomTabView.as_view(), name='room-tab'),
    path('join/room/<str:room_pk>/', views.JoinRoomView.as_view(), name='join-room'),
    path('leave/room/<str:room_pk>/', views.LeaveRoomView.as_view(), name='leave-room'),
    path('manage/room/<str:room_pk>/', views.ManageRoomView.as_view(), name='manage-room'),
    path('accept/invite/<str:room_pk>/', views.AcceptRoomInviteView.as_view(), name='accept-room-invite'),
    path('accept/<str:room_pk>/<str:username>/', views.AcceptRoomGuestView.as_view(), name='accept-room-guest'),
    path('modal/search/room/', views.ModalSearchRoomView.as_view(), name='search-room'),
    path('invite/room/<str:room_pk>/', views.RoomInviteView.as_view(), name='invite-room'),
    path('create-room/', views.CreateRoomView.as_view(), name='create-room'),
    path('delete/room/<str:room_pk>/', views.DeleteRoomView.as_view(), name='delete-room'),
    path('manage/room-authority/<str:room_pk>/', views.ManageRoomAuthorityView.as_view(), name='manage-room-authority'),
    path('manage/room-display/<str:room_pk>/', views.ManageRoomDisplayView.as_view(), name='manage-room-display'),
    path('manage/room-tab/<str:room_pk>/', views.ManageRoomTabView.as_view(), name='manage-room-tab'),
    path('manage/room-participant/<str:room_pk>/', views.ManageRoomParticipantView.as_view(), name='manage-room-participant'),
    path('manage/room-reply-type/<str:room_pk>/', views.ManageRoomPostView.as_view(), name='manage-room-reply-type'),
    path('manage/room-information/<str:room_pk>/', views.ManageRoomRequestInformationView.as_view(), name='manage-room-information'),
    path('manage/room-personal/<str:room_pk>/', views.ManageRoomPersonalView.as_view(), name='manage-room-personal'),

    # Follow
    path('follow/<str:username>/', views.FollowView.as_view(), name='follow-user'),
    path('block/<str:username>/', views.BlockView.as_view(), name='block-user'),

    # Post
    path('post/', views.PostView.as_view(), name='post'),
    path('post/<str:post_pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<str:post_pk>/reply/', views.ReplyPostView.as_view(), name='reply-post'),
    # path('post/edit/<str:post_pk>/', views.PostEditView.as_view()), 
    path('post/delete/<str:post_pk>/', views.PostDeleteView.as_view(), name='delete-post'),
    path('post/agree/<str:post_pk>/', views.PostAgreeView.as_view(), name='agree-post'),
    path('post/favorite/<str:post_pk>/', views.PostFavoriteView.as_view(), name='favorite-post'),
    path('post/demagogy/<str:post_pk>/', views.PostDemagogyView.as_view(), name='demagogy-post'),

    # Reply
    path('reply/<str:reply_pk>/', views.ReplyDetailView.as_view(), name='reply-detail'),
    path('reply/<str:reply_pk>/reply/', views.ReplyReplyView.as_view(), name='reply-reply'),
    path('reply/delete/<str:reply_pk>/', views.ReplyDeleteView.as_view(), name='delete-reply'),
    path('reply/agree/<str:reply_pk>/', views.ReplyAgreeView.as_view(), name='agree-reply'),
    path('reply/favorite/<str:reply_pk>/', views.ReplyFavoriteView.as_view(), name='favorite-reply'),
    path('reply/demagogy/<str:reply_pk>/', views.ReplyDemagogyView.as_view(), name='demagogy-reply'),

    # Reply2
    path('reply2/delete/<str:reply2_pk>/', views.Reply2DeleteView.as_view(), name='delete-reply2'),
    path('reply2/agree/<str:reply2_pk>/', views.Reply2AgreeView.as_view(), name='agree-reply2'),
    path('reply2/favorite/<str:reply2_pk>/', views.Reply2FavoriteView.as_view(), name='favorite-reply2'),
    path('reply2/demagogy/<str:reply2_pk>/', views.Reply2DemagogyView.as_view(), name='demagogy-reply2'),

    # Error
    path('error/', views.ShowErrorView.as_view(), name='error'),
    
    path('', views.IndexRoomListView.as_view(), name='top'),
    path('rooms/', views.IndexRoomListView.as_view(), name='rooms'),
    path('posts/', views.IndexPostListView.as_view(), name='posts'),
    path('users/', views.IndexUserListView.as_view(), name='users'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]