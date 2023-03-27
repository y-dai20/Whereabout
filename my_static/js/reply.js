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