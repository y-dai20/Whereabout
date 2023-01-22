from django.views.generic import View

from base.views.functions import is_str, is_empty
from base.models.room_models import Room, RoomUser

class ValidateRoomView(View):
    def __init__(self, room):
        super().__init__()
        self.error_messages = []
        if is_str(room):
            self.room = Room.objects.get_or_none(id=room, is_deleted=False)
        elif isinstance(room, Room):
            self.room = room
        else:
            self.room = None

    def get_error_messages(self):
        return self.error_messages

    def is_user(self, user):
        return not is_empty(user) and user.is_authenticated

    def is_room_exist(self):
        return not is_empty(self.room)

    def is_room_user(self, user):
        if not self.is_room_exist() or not self.is_user(user):
            return False

        if self.is_admin(user):
            return True

        return RoomUser.objects.filter(room=self.room, user=user, is_deleted=False, is_blocked=False).exists()

    def is_user_blocked(self, user):
        if not self.is_room_exist() or not self.is_user(user):
            return None
        
        if RoomUser.objects.filter(room=self.room, user=user, is_deleted=False, is_blocked=True).exists():
            return True

        return False

    def is_admin(self, user):
        if not self.is_room_exist() or not self.is_user(user):
            return False

        return self.room.admin == user

    def can_access(self, user):
        if self.is_admin(user):
            return True
        if self.is_room_user(user):
            return True
        if self.is_room_exist() and self.room.is_public:
            return True
        return False

    def can_reply(self, user):
        if not self.is_user(user):
            return False
        if not self.is_room_exist() or self.is_admin(user):
            return True
        if RoomUser.objects.filter(room=self.room, user=user, authority__can_reply=True, is_deleted=False, is_blocked=False).exists():
            return True

        return False

    def can_post(self, user):
        if not self.is_user(user):
            return False
        if self.is_admin(user) or not self.is_room_exist():
            return True
        if RoomUser.objects.filter(room=self.room, user=user, authority__can_post=True, is_deleted=False, is_blocked=False).exists():
            return True

        return False

    def get_room(self):
        if not self.is_room_exist():
            return None
        
        return self.room

    def is_public(self):
        if not self.is_room_exist():
            return None

        return self.room.is_public

    def need_approval(self):
        if not self.is_room_exist():
            return None

        return self.room.need_approval

    def validate_base(self, user):
        if not self.is_user(user):
            self.error_messages.append('ログインが必要です')
            return False

        if not self.is_room_exist():
            return True
        
        if not self.is_room_user(user):
            self.error_messages.append('返信するためにはルームに参加する必要があります')
            return False

        return True

    def validate_post(self, user):
        if not self.validate_base(user):
            return False

        if not self.can_post(user):
            self.error_messages.append('このルームで投稿する権限がありません')
            return False

        return True

    def validate_reply(self, user):
        if not self.validate_base(user):
            return False

        if not self.can_reply(user):
            self.error_messages.append('このルームで返信する権限がありません')
            return False

        return True