from base.views.functions import get_json_message

def empty_error():
    return get_json_message(False, 'エラー', ['エラーが発生しました．(E01)'])
