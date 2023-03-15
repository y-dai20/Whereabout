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

urlpatterns = [
    path('admin/', admin.site.urls),

    # Get
    path('get/room-tab-items/', views.GetRoomTabItems.as_view()),
    path('get/reply/', views.GetReplyView.as_view()),
    path('get/reply2/', views.GetReply2View.as_view()),
    path('get/tag/', views.GetTag.as_view()),
    path('get/reply-types/post/<str:post_pk>/', views.GetPostReplyTypesView.as_view()),
    path('get/reply-types/reply/<str:reply_pk>/', views.GetReplyReplyTypesView.as_view()),
    path('get/user/<str:username>/', views.GetUserView.as_view()),
    path('get/room/<str:room_pk>/', views.GetRoomView.as_view()),
    path('get/room-request-information/<str:room_pk>/', views.GetRoomRequestInformationView.as_view()),

    # Account
    path('login/', views.LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', views.SendMailForSignupView.as_view()),
    path('signup/<str:one_time_id>/', views.SignUpView.as_view()),
    path('change-password/', views.ChangePasswordView.as_view()),
    path('reset-password/', views.SendMailForResetPasswordView.as_view()),
    path('reset-password/<str:one_time_id>/', views.ResetPasswordView.as_view()),
    path('profile/', views.UserProfileView.as_view()),
    path('modal/search/user/', views.ModalSearchUserView.as_view()),

    # Room
    path('room/<str:room_pk>/', views.ShowRoomView.as_view()),
    path('room/good/<str:room_pk>/', views.RoomGoodView.as_view()),
    path('room/information/<str:room_pk>/', views.RoomInformationView.as_view()),
    path('room/<str:room_pk>/<str:room_tab_pk>/', views.ShowRoomTabView.as_view()),
    path('join/room/<str:room_pk>/', views.JoinRoomView.as_view()),
    path('leave/room/<str:room_pk>/', views.LeaveRoomView.as_view()),
    path('manage/room/<str:room_pk>/', views.ManageRoomView.as_view()),
    path('accept/invite/<str:room_pk>/', views.AcceptRoomInviteView.as_view()),
    path('accept/<str:room_pk>/<str:username>/', views.AcceptRoomGuestView.as_view()),
    path('modal/search/room/', views.ModalSearchRoomView.as_view()),
    path('invite/room/<str:room_pk>/', views.RoomInviteView.as_view()),
    path('create-room/', views.CreateRoomView.as_view()),
    path('delete/room/<str:room_pk>/', views.DeleteRoomView.as_view()),
    path('manage/room-authority/<str:room_pk>/', views.ManageRoomAuthorityView.as_view()),
    path('manage/room-display/<str:room_pk>/', views.ManageRoomDisplayView.as_view()),
    path('manage/room-tab/<str:room_pk>/', views.ManageRoomTabView.as_view()),
    path('manage/room-participant/<str:room_pk>/', views.ManageRoomParticipantView.as_view()),
    path('manage/room-reply-type/<str:room_pk>/', views.ManageRoomPostView.as_view()),
    path('manage/room-information/<str:room_pk>/', views.ManageRoomRequestInformationView.as_view()),
    path('manage/room-personal/<str:room_pk>/', views.ManageRoomPersonalView.as_view()),

    # Follow
    path('follow/<str:username>/', views.FollowView.as_view()),
    path('block/<str:username>/', views.BlockView.as_view()),

    # Post
    path('post/', views.PostView.as_view()),
    path('post/<str:post_pk>/', views.PostDetailView.as_view(), name="post_detail"),
    path('post/<str:post_pk>/reply/', views.ReplyPostView.as_view()),
    # path('post/edit/<str:post_pk>/', views.PostEditView.as_view()), 
    path('post/delete/<str:post_pk>/', views.PostDeleteView.as_view()),
    path('post/agree/<str:post_pk>/', views.PostAgreeView.as_view()),
    path('post/favorite/<str:post_pk>/', views.PostFavoriteView.as_view()),
    path('post/demagogy/<str:post_pk>/', views.PostDemagogyView.as_view()),

    # Reply
    path('reply/<str:reply_pk>/', views.ReplyDetailView.as_view()),
    path('reply/<str:reply_pk>/reply/', views.ReplyReplyView.as_view()),
    path('reply/delete/<str:reply_pk>/', views.ReplyDeleteView.as_view()),
    path('reply/agree/<str:reply_pk>/', views.ReplyAgreeView.as_view()),
    path('reply/favorite/<str:reply_pk>/', views.ReplyFavoriteView.as_view()),
    path('reply/demagogy/<str:reply_pk>/', views.ReplyDemagogyView.as_view()),

    # Reply2
    path('reply2/delete/<str:reply2_pk>/', views.Reply2DeleteView.as_view()),
    path('reply2/agree/<str:reply2_pk>/', views.Reply2AgreeView.as_view()),
    path('reply2/favorite/<str:reply2_pk>/', views.Reply2FavoriteView.as_view()),
    path('reply2/demagogy/<str:reply2_pk>/', views.Reply2DemagogyView.as_view()),

    # Error
    path('error/', views.ShowErrorView.as_view()),
    
    path('', views.IndexRoomListView.as_view()),
    path('posts/', views.IndexPostListView.as_view()),
    path('user/', views.IndexUserListView.as_view()),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]