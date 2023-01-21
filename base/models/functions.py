from gettext import install
from django.conf import settings
from django.utils.crypto import get_random_string
import uuid

def create_id():
    return get_random_string(settings.ID_LENGTH)

def pptx_img_directory_path(instance, filename):
    return 'pptx/' + str(uuid.uuid4()) + '/' + get_img_name(filename)

def post_directory_path(instance, filename):
    return 'post/' + img_directory_path(instance, filename)

def room_directory_path(instance, filename):
    return 'room/' + img_directory_path(instance, filename)

def img_directory_path(instance, filename):
    return 'images/' + get_img_name(filename)

def video_directory_path(instance, filename):
    return 'videos/' + get_img_name(filename)

def get_img_name(filename):
    return '{}.{}'.format(str(uuid.uuid4()), filename.split('.')[-1])