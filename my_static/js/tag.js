$(document).ready(function() {
    $('.tag-input').on('keyup keydown', function() {
        var self = this;
        if (self.timer) {
            clearTimeout(self.timer);
        }
        self.timer = setTimeout(function(){
            self.timer = null;
            var val = $(self).val();
            $.ajax({
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
    var item = $(this).data('item');
    if (!is_empty(item) & url.pathname != `/${item}/`) {
        window.location.href = `/${item}/?tags=${$(this).text()}`;
        return false;
    }
    
    var params = url.searchParams;
    params.set('tags', [params.get('tags'), $(this).text()].join(','));
    url.search = params.toString();
    window.location.href = url.toString();
});