$(document).ready(function() {
    $('.tag-input').on('keyup keydown', function() {
        var self = this;
        if (!is_empty(self.timer)) {
            clearTimeout(self.timer);
        }
        self.timer = setTimeout(function(){
            self.timer = null;
            var val = $(self).val();
            $.ajax({
                //todo url
                url:'/get/tag/',
                type:'POST',
                data:{'tag':val},
                timeout:60000,
            }).done(function (data) {
                var html = '';
                $.each(data.candidates, function(idx, candidate) {
                    html += get_option(candidate);
                });
                $(self).siblings('datalist').html(html);
            }).fail(function (data) {
                show_modal_message(data.status, [data.statusText]);
            });
        }, 1000);
    });

    $('.add-tag-button').click(function() {
        var val = $(this).siblings('.tag-input').val();
        if (is_empty(val)) {
            return false;
        }
        var tag_len = $(this).siblings('.added-tag-list').find('.tag-item').length + 1;
        var max_len = $(this).data('max-len');
        if (tag_len > max_len) {
            show_modal_message('警告', [`タグは最大${max_len}個までです。`, `新規追加したい場合は既存のタグをクリックして削除してください。`])
            return false;
        }

        append_removable_tag(val, $(this).siblings('.added-tag-list'));
        $(this).siblings('.tag-input').val('');
    });
});

$(document).on('click', '.removable-tag-item', function() {
    var val = $(this).text();
    var input_tags = $(this).parent('.added-tag-list').siblings('input[name="tags"]');
    var tags = input_tags.val().split(',');
    tags.splice(tags.indexOf(val), 1);
    input_tags.val(tags.join(','));
    $(this).remove();
});

$(document).on('click', '.tag-link-button', function() {
    var url = new URL(window.location.href);
    var url = $(this).data('url');
    var tag = $(this).text();
    if (!is_empty(url) & url.pathname != url) {
        window.location.href = `${url}?tags=${tag}`;
        return false;
    }

    if ($('#added-search-post-tag-list').length > 0) {
        append_removable_tag(tag, '#added-search-post-tag-list');
        var new_url = set_url_parameter(get_form_href('search-post-form'), 'tags', tag);
        search_post_ajax(new_url);
    } else if ($('#added-search-pir-tag-list').length > 0) {
        append_removable_tag(tag, '#added-search-pir-tag-list');
        var new_url = set_url_parameter(get_form_href('search-post-form'), 'tags', tag);
        search_post_ajax(new_url);
    } else if ($('#added-search-user-tag-list').length > 0) {
        append_removable_tag(tag, '#added-search-user-tag-list');
        var new_url = set_url_parameter(get_form_href('search-user-form'), 'tags', tag);
        search_user_ajax(new_url);
    } else if ($('#added-search-room-tag-list').length > 0) {
        append_removable_tag(tag, '#added-search-room-tag-list');
        var new_url = set_url_parameter(get_form_href('search-room-form'), 'tags', tag);
        search_room_ajax(new_url);
    } else {
        window.location.href = set_url_parameter(url, 'tags', tag);
    }
});