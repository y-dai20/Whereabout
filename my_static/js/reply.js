$(document).on('click', '.get-reply2-link', function() {
    var obj = get_item_data($(this));
    if ($('.reply-detail-link').data('obj-id') == obj.id) {
        return false;
    }

    $('.index-post-reply2-sidebar').removeClass('not-display');
    $('.reply2-list').html($(this).clone());
    //todo url
    $('.reply-detail-link').html(`<a href="/reply/${obj.id}/" role="button" type="button" class="btn btn-secondary sidebar-button">返信へ移動</a>`)
    $('.reply-detail-link').data('obj-id', obj.id);

    $.ajax({
        url: `/get/reply2/`,
        type:'POST',
        data:{obj_id:obj.id},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        create_replies(data.items);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });

    function create_replies(items) {
        create_reply_items('.reply2-list', items, false);
        $('.reply2-list').parents('.sidebar-item').find('.load-more-button').show();
        $('.reply2-list').parents('.sidebar-item').find('.load-more-button').data('idx', 1);
    }
});

$(document).on('click', '.get-reply-link', function() {
    var obj = get_item_data($(this));
    if ($('.post-detail-link').data('obj-id') == obj.id) {
        return false;
    }

    close_sidebar();
    $('.index-post-reply-sidebar').removeClass('not-display');
    add_class($('.index-post-reply2-sidebar'), 'not-display');

    $('.reply-list').html($(this).clone());
    //todo url
    $('.post-detail-link').html(`<a href="/post/${obj.id}/" role="button" type="button" class="sidebar-button btn btn-secondary">投稿へ移動</a>`)
    $('.post-detail-link').data('obj-id', obj.id);
    $.ajax({
        url: `/get/reply/`,
        type:'POST',
        data:{obj_id:obj.id},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        create_replies(data.items);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });

    function create_replies(items) {
        create_reply_items('.reply-list', items, true);
        $('.reply-list').parents('.sidebar-item').find('.load-more-button').show();
        $('.reply-list').parents('.sidebar-item').find('.load-more-button').data('idx', 1);
    }
});

$('#submit-reply-button').on('click', function(event) {
    event.preventDefault();
    var form = `reply-form`;
    if (!form_valid(form)) {
        return false;
    }
    
    var fd = get_img_preview_files('reply');
    fd = get_form_data('reply-form', ['input', 'textarea', 'select'], fd);
    $.ajax({
        url:$(this).data('url'),
        type:'POST',
        data:fd,
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        close_modal('modal-reply');
        show_modal_message(data.title, data.message);
        
        if (data.reply.obj_type == 'reply') {
            var item_data = get_item_data($('.index-post-reply-sidebar').find(`.reply-list`).find(`.post-item`));
            if (is_empty(item_data) | item_data.id != data.reply.post_id) {
                return true;
            }
            $('.index-post-reply-sidebar').find(`.reply-list`).append(get_reply_item(data.reply, true));
            active_luminous(data.reply.obj_id);
        } else if (data.reply.obj_type == 'reply2') {
            var item_data = get_item_data($('.index-post-reply2-sidebar').find(`.reply2-list`).find(`.reply-item`));
            if (is_empty(item_data) | item_data.id != data.reply.reply_id) {
                return true;
            }
            $('.index-post-reply2-sidebar').find(`.reply2-list`).append(get_reply_item(data.reply));
            active_luminous(data.reply.obj_id);
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});