from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.timezone import make_aware, make_naive
from django.http import JsonResponse

import ast
import magic
import os
import math
from datetime import datetime

def create_id(length):
    return get_random_string(length)

def get_upload_mimetype(file):
    return magic.from_buffer(file.read(), mime=True)

def get_mimetype(path):
    return magic.from_file(path, mime=True)

def is_upload_file(type, file):
    if type == 'img':
        return is_uploaded_file_img(file)
    elif type == 'video':
        return is_uploaded_file_video(file)

    return None

def is_uploaded_file_img(file):
    if not get_upload_mimetype(file).startswith('image'):
        return False
    if os.path.splitext(file.name.lower())[1] not in ['.jpg', '.jpeg', '.png', '.ico', '.bmp']:
        return False
    return True

def is_uploaded_file_video(file):
    if not get_upload_mimetype(file).startswith('video'):
        return False
    if os.path.splitext(file.name.lower())[1] not in ['.mp4']:
        return False
    return True

def get_reply_types():
    return ['つぶやき', '根拠', '確認', '要求', '予想', '回答', '質問', '補足', '証拠', 'その他']

def get_list_index(list, val):
    if val not in list:
        return -1
    return str(list.index(val))

def get_img_path(img_field):
    return settings.MEDIA_URL + str(img_field) if img_field else None

def get_list_item(list, idx, is_strip=True):
    res = list[idx] if len(list) > idx else ''
    if is_strip and is_str(res):
        res = res.strip()
    return res

def get_list_item_list(list, idx):
    return list[idx] if len(list) > idx else []

def get_list_item_dict(list, idx):
    return list[idx] if len(list) > idx else {}

def get_dict_item(dict, key, is_strip=True):
    res = dict[key] if key in dict else ''
    if is_strip and is_str(res):
        res = res.strip()
    return res

def get_dict_item_list(dict, key):
    return dict[key] if key in dict else []

def get_dict_item_dict(dict, key):
    return dict[key] if key in dict else {}

def literal_eval(str):
    if is_empty(str):
        return ''
    return ast.literal_eval(str)

def is_all_none(list):
    for l in list:
        if l is not None or l != '':
            return False
    return True

def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == '':
        return True
    if isinstance(value, (dict, list)) and len(value) < 1:
        return True
    
    return False

def is_same_empty_count(list, allow_empty_count=1):
    empty_count = 0
    for l in list:
        empty_count += 1 if is_empty(l) else 0
    
    return True if empty_count == allow_empty_count else False

def get_boolean_or_none(value):
    if is_str(value):
        value = value.strip().lower()
        if value == 'true' or value == 'y':
            return True
        if value == 'false' or value == 'n':
            return False
    elif is_bool(value):
        return value
    return None

def is_str(value):
    if type(value) is str:
        return True
    return False

def is_int(value):
    if is_empty(value):
        return False
    if type(value) is int:
        return True
    if is_str(value) and value.isdecimal():
        return True
    return False

def is_bool(value):
    if is_empty(value):
        return False
    if type(value) is bool:
        return True
    return False

def get_bool_or_str(value):
    if is_str(value):
        if value.strip().lower() == 'true':
            return True
        if value.strip().lower() == 'false':
            return False
    elif is_bool(value):
        return value
    return value

def get_display_datetime(dt):
    days = dt.days
    if days < 1:
        seconds = dt.seconds
        if seconds < 60:
            return '{}秒前'.format(seconds)
        if seconds < 3600:
            return '{}分前'.format(seconds // 60)
        return '{}時間前'.format(seconds // 3600)

    if days < 7:
        return '{}日前'.format(days)
    if days < 30:
        return '{}週間前'.format(days // 7)
    if days < 365:
        return '{}ヶ月前'.format(days // 30)
    return '{}年前'.format(days // 365)

def get_json_message(is_success:bool, title='', messages=[], add_dict={}):
    return {'is_success':is_success, 'title':title, 'message':messages, **add_dict}
def get_json_success_message(messages=[], add_dict={}):
    return get_json_message(True, '成功', messages, add_dict)
def get_json_error_message(messages=[], add_dict={}):
    return get_json_message(False, 'エラー', messages, add_dict)

def get_file_size_by_unit(byte:int, unit='MB'):
    unit = unit.upper()
    assert unit in ['B', 'KB', 'MB', 'GB']
    byte = float(byte)
    if unit == 'KB':
        byte = byte / 1024
    elif unit == 'MB':
        byte = byte / (1024**2)
    elif unit == 'GB':
        byte = byte / (1024**3)
    
    return str(math.ceil(byte * 10) / 10) + unit

def get_combined_list(name1:str, list1:list, name2:str, list2:list):
    combined_list = []
    len1 = len(list1)
    len2 = len(list2)
    for i in range(max(len1, len2)):
        combined_list.append({
            name1:list1[i] if i < len1 else None,
            name2:list2[i] if i < len2 else None,
        })
    return combined_list

def get_diff_seconds_from_now(model_time):
    return (datetime.now() - make_naive(model_time)).seconds

def get_unit_time(seconds, unit):
    assert unit in ['秒', '分', '時間', '日']
    if unit == '分':
        unit = unit / 60
    elif unit == '時間':
        unit = unit / (60**2)
    elif unit == '日':
        unit = unit / (60**3)

    return str(math.ceil(seconds * 10) / 10) + unit

def get_form_error_message(form):
    messages = []
    for key, value in form.errors.items():
        for v in value:
            messages.append(v)
    return messages

def get_json_error(status):
    return JsonResponse(get_json_error_message(['{}'.format(status)]), status=status)

def get_number_unit(num):
    if num >= 1000000000:
        return str(get_first_decimal_point(num / 1000000000)) + 'B'
    elif num >= 1000000:
        return str(get_first_decimal_point(num / 1000000)) + 'M'
    elif num >= 1000:
        return str(get_first_decimal_point(num / 1000)) + 'K'
    
    return num

def get_first_decimal_point(num):
    if num >= 10:
        return math.ceil(num)
    return math.ceil(num * 10) / 10

def get_exist_files_dict(files):
    exist_files = {}
    for file in files:
        if not bool(file):
            continue
        exist_files[get_img_path(file.name)] = file.file
    return exist_files

def get_img_list(form_data, files, max_img=1, exist_files={}):
    files.update(get_exist_files_dict(exist_files))
    return get_file_list('img', form_data, files, max_img)

def get_video_list(form_data, files, max_video=1, exist_files={}):
    files.update(get_exist_files_dict(exist_files))
    return get_file_list('video', form_data, files, max_video)

def get_file_list(type, form_data, files, max_files=1):
    file_names = get_dict_item(form_data, type + '_file_names').split(',')
    file_list = []
    for idx in range(max_files):
        file_name = get_list_item(file_names, idx)
        if file_name in files and (is_upload_file(type, files[file_name]) or os.path.isfile(str(files[file_name]))):
            file_list.append(files[file_name])
            continue
        file_list.append(None)

    return file_list

def get_file_size(files):
    total_size = 0
    for file in files:
        if is_empty(file):
            continue
        total_size += file.size
    
    return total_size