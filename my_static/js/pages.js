$(document).ready(function(){
    $('.select-post-room').select2({
        dropdownParent: $('#modal-post'),
        language: 'ja',
    });
    $('.manage-room-img-preview-list').sortable();
    $('.manage-room-img-preview-list').disableSelection();
    toggle_need_approval($('#manage-room-approval'), 'manage-room-approval-label');
    toggle_is_public($('#manage-room-public'), 'manage-room-public-label');
});

$(function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

function get_item_data(target) {
    if (is_empty(target)) {
        return {};
    }

    if (!target.hasClass('footer-button')) {
        if (target.parents('.footer-button').length > 0) {
            target = target.parents('.footer-button');
        } else if (target.find('.footer-button').length > 0) {
            target = target.find('.footer-button');
        } else if (target.parents('.item-object').length > 0) {
            target = target.parents('.item-object').find('.footer-button');
        }
    }
    var res = target.data();
    res.footer = target;
    res.item = target.parents('.item-object');
    return res;
}

function is_error(data) {
    if (!data.is_success) {
        show_modal_message(data.title, data.message);
        return true;
    }
    return false;
}

function ajax_agree(target, is_agree) {
    var obj = get_item_data(target);
    $.ajax({
        url: `/${obj.type}/agree/${obj.id}/`,
        type:'GET',
        data:{is_agree:is_agree},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        if (data['is_agree'] & !data['is_deleted']) {
            obj.footer.children('.agree-btn').removeClass("btn-outline-success").addClass("btn-success");
            obj.footer.children('.disagree-btn').removeClass("btn-danger").addClass("btn-outline-danger");
        } else if (!data['is_agree'] & !data['is_deleted']) {
            obj.footer.children('.agree-btn').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.disagree-btn').removeClass("btn-outline-danger").addClass("btn-danger");
        } else {
            obj.footer.children('.agree-btn').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.disagree-btn').removeClass("btn-danger").addClass("btn-outline-danger");
        }

        obj.footer.children('.agree-count').text(data['agree_count']);
        obj.footer.children('.disagree-count').text(data['disagree_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
//todo 複製しているなら同期を取るようにする
$(document).on('click', '.agree-btn', function(){
    ajax_agree($(this), true);
});
$(document).on('click', '.disagree-btn', function(){
    ajax_agree($(this), false);
});

function ajax_good(target, is_good) {
    var obj = get_item_data(target);
    $.ajax({
        url: `/${obj.type}/good/${obj.id}/`,
        type:'GET',
        data:{is_good:is_good},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        
        if (data['is_good'] & !data['is_deleted']) {
            obj.footer.children('.good-btn').removeClass("btn-outline-success").addClass("btn-success");
            obj.footer.children('.bad-btn').removeClass("btn-danger").addClass("btn-outline-danger");
        } else if (!data['is_good'] & !data['is_deleted']) {
            obj.footer.children('.good-btn').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.bad-btn').removeClass("btn-outline-danger").addClass("btn-danger");
        } else {
            obj.footer.children('.good-btn').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.bad-btn').removeClass("btn-danger").addClass("btn-outline-danger");
        }
        obj.footer.children('.good-count').text(data['good_count']);
        obj.footer.children('.bad-count').text(data['bad_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
$(document).on('click', '.good-btn', function(){
    ajax_good($(this), true);
});
$(document).on('click', '.bad-btn', function(){
    ajax_good($(this), false);
});

function ajax_demagogy(target, is_true) {
    var obj = get_item_data(target);
    $.ajax({
        url: `/${obj.type}/demagogy/${obj.id}/`,
        type:'GET',
        data:{is_true:is_true},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        if (data['is_true'] & !data['is_deleted']) {
            obj.footer.children('.demagogy-btn').removeClass("btn-outline-dark").addClass("btn-dark");
            obj.footer.children('.disdemagogy-btn').removeClass("btn-dark").addClass("btn-outline-dark");
        } else if (!data['is_true'] & !data['is_deleted']) {
            obj.footer.children('.demagogy-btn').removeClass("btn-dark").addClass("btn-outline-dark");
            obj.footer.children('.disdemagogy-btn').removeClass("btn-outline-dark").addClass("btn-dark");
        } else {
            obj.footer.children('.demagogy-btn').removeClass("btn-dark").addClass("btn-outline-dark");
            obj.footer.children('.disdemagogy-btn').removeClass("btn-dark").addClass("btn-outline-dark");
        }
        
        obj.footer.children('.true-count').text(data['true_count']);
        obj.footer.children('.false-count').text(data['false_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
$(document).on('click', '.demagogy-btn', function(){
    ajax_demagogy($(this), true);
});
$(document).on('click', '.disdemagogy-btn', function(){
    ajax_demagogy($(this), false);
});

$(document).on('click', '.favorite-btn', function(){
    var img = $(this).children('.favorite-img');
    var obj = get_item_data($(this));

    $.ajax({
        url: `/${obj.type}/favorite/${obj.id}/`,
        type:'GET',
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        if (data['is_favorite']) {
            img.attr('src', function(i, e){
                return e.replace(IMGS.whiteStar, IMGS.yellowStar)
            });
        } else {
            img.attr('src', function(i, e){
                return e.replace(IMGS.yellowStar, IMGS.whiteStar)
            });
        }

        obj.footer.children('.favorite-count').text(data['favorite_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.follow-btn', function(){
    var obj = get_item_data($(this));
    var btn = $(this);
    $.ajax({
        url: follow_url(obj.username),
        type:'POST',
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        var count = btn.siblings('.followed-count');
        if (data['is_follow']) {
            btn.removeClass('btn-outline-secondary').addClass('btn-secondary').text('フォロー解除');
            count.text(parseInt(count.text()) + 1);
        } else {
            btn.removeClass('btn-secondary').addClass('btn-outline-secondary').text('フォロー');
            count.text(parseInt(count.text()) - 1);
        } 
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.block-btn', function(){
    var obj = get_item_data($(this));
    $.ajax({
        url: block_url(obj.username),
        type:'POST',
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        obj.footer.html(get_user_footer(data));
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('.save-confirm-btn').on('click', function(){
    show_modal_message('確認', ['保存しますか'], get_confirm_button('保存', $(this).data('selector'), $(this).data('url')));
});
$('.cancel-confirm-btn').on('click', function(){
    show_modal_message('確認', ['変更内容をキャンセルしますか'], '<a onclick="location.reload()" type="button" class="btn btn-danger" data-bs-dismiss="modal">キャンセル</a>');
});

$('input, textarea').on('click change input', function() {
    set_char_len(
        target=$(this).siblings('.char-len'), 
        len=$(this).val().length, 
        max_len=$(this).data('max-len')
    );
});

function set_char_len(target, len, max_len, min_len=0) {
    target.text(`${len}文字`);
    if (len > max_len || len < min_len) {
        add_class(target, 'c-red');
        target.removeClass('c-green');
    } else {
        add_class(target, 'c-green');
        target.removeClass('c-red');
    }
}

$(document).on('change', '.user-img-img-preview-uploader', function() {
    $('.user-img').hide();
    var file = this.files[0];
    var fileReader = new FileReader();
    fileReader.onload = (function (e) {
        $('.user-img-area').prepend(get_img_preview_html(e.target.result, 'user-img', file.name, file.size, 0, false));
    });
    fileReader.readAsDataURL(file);
    $('#user-img-img-upload-size').data('size', 0);
    set_upload_file_size('user-img', 'img', file.size, MAX_USER_IMG_BYTE);
});
$(document).on('change', '.post-img-preview-uploader', function() {
    $('#post-form-video').hide();
    preview_upload('img', this.files, 'post', MAX_POST_IMGS, MAX_POST_IMG_BYTE);
});
$(document).on('click', '.post-img-delete-button', function(){
    delete_img_preview($(this), 'post', MAX_POST_IMG_BYTE);
    if ($('.post-img-preview-list div').length == 0) {
        $('#post-form-video').show();
    }
});
$(document).on('change', '.post-video-preview-uploader', function() {
    $('#post-form-img').hide();
    preview_upload('video', this.files, 'post', MAX_POST_VIDEOS, MAX_POST_VIDEO_BYTE);
});
$(document).on('click', '.post-video-delete-button', function(){
    delete_video_preview($(this), 'post', MAX_POST_VIDEO_BYTE);
    if ($('.post-video-preview-list div').length == 0) {
        $('#post-form-img').show();
    }
});

var deleteObject;
$(document).on('click', '.delete-button', function(){
    var url = $(this).data('url');

    $.ajax({
        url:url,
        type:'POST',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }

        close_modal('modal-message');
        show_modal_message(data.title, data.message);
        if (!is_empty(deleteObject)) {
            deleteObject.hide();
        }
        if (data.href) {
            window.location.href = data.href;
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.delete-confirm-button', function() {
    var obj = get_item_data($(this));
    var url = `/${obj.type}/delete/${obj.id}/`;
    deleteObject = obj.item;
    var footer = `<button type="button" class="delete-button btn btn-danger" data-url="${url}">削除</button>`;
    show_modal_message('確認', ['削除しますか'], footer);
});

$(document).on('click', '.load-more-button', function() {
    var idx = $(this).data('idx');
    var type = $(this).data('type');
    var target = $(this);
    if (['reply', 'reply2'].includes(type)) {
        var url = `/get/${type}/`;
        var data = {
            'idx':idx, 
            'obj_id':$(this).parents('.sidebar-item').prev().find('.obj-link').data('obj-id')
        };
    } else {
        var url = location.href;
        var data = {'idx':idx}; 
    }

    $.ajax({
        url:url,
        type:'POST',
        data:data,
        timeout:60000,
    }).done(function(data){
        if (is_error(data)) {
            return false;
        }

        target.data('idx', data.idx);
        if (type == 'post') {
            create_post_items('.post-list', data.items, true);
            hide_load_more('.post-list', data);
        } else if (type == 'room') {
            create_room_items('.room-list', data.items);
            hide_load_more('.room-list', data);
        } else if (type == 'user') {
            create_user_items('.user-list', data.items);
            hide_load_more('.user-list', data);
        } else if (type == 'reply') {
            create_reply_items('.reply-list', data.items, true);
            hide_load_more('.reply-list', data);
        } else if (type == 'reply2') {
            create_reply_items('.reply2-list', data.items, true);
            hide_load_more('.reply2-list', data);
        } else if (type == 'post-detail') {
            create_post_detail_items('.post-detail-list', data.items, true);
            hide_load_more('.post-detail-list', data);
        } else if (type == 'reply-detail') {
            create_post_detail_items('.reply-detail-list', data.items, true);
            hide_load_more('.reply-detail-list', data);
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });

    function hide_load_more(list_cls, data) {
        if (data.is_end) {
            $(list_cls).siblings('.load-more').find('.load-more-button').hide();
        }
    }
});

function close_sidebar() {
    $('.sidebar').each(function(){
        add_class($(this), 'not-display');
    });
    $('.sidebar-menu').each(function(){
        $(this).removeClass('open');
    });
    $('.hamburger-menu').each(function(){
        $(this).removeClass('open');
    });
}

$('.sidebar-menu').click(function(e) {
    e.stopPropagation();
    var target = $(this).data('for');
    $(this).toggleClass('open');
    $(`.${target}`).toggleClass('not-display');

    $(this).siblings('.sidebar-menu').each(function() {
        var target1 = $(this).data('for');
        add_class($(`.${target1}`), 'not-display');
        $(this).removeClass('open');
    });
    
    if ($(`.${target}`).hasClass('right-sidebar')) {
        $(`.${target}`).siblings('.right-sidebar').each(function(){
            add_class($(this), 'not-display');
        });
    } else if ($(`.${target}`).hasClass('left-sidebar')) {
        $(`.${target}`).siblings('.left-sidebar').each(function(){
            add_class($(this), 'not-display');
        });
    }
});

$('.hamburger-menu').click(function(e){
    e.stopPropagation();
    var target = $(this).data('for');
    $(this).toggleClass('open');
    $(`.${target}`).toggleClass('not-display');
});

$(document).on('click', '.open-new-window-btn', function() {
    window.open(URLS.base + $(this).data('url'), '_blank')
});

$('.clear-input-btn').on('click', function(){
    $(this).parents('form').find('input[type="text"]').each(function(){
        $(this).val('');
    });
});

$(document).on('change', '.validate-length', function() {
    validate_length($(this), $(this).val(), $(this).data('min-len'), $(this).data('max-len'));
});
$(document).on('change', '.validate-num', function() {
    validate_num($(this), $(this).val(), $(this).data('min-len'), $(this).data('max-len'));
});
$(document).on('change', '.validate-integer', function() {
    validate_integer($(this), $(this).val());
});

$(document).on('click', '.copy-link', function() {
    navigator.clipboard.writeText($(this).data('link'));

    $(this).tooltip({
        title: 'リンクをコピーしました',
        placement: 'top',
        trigger: 'manual'
    }).on('shown.bs.tooltip', function(){
        setTimeout((function(){
            $(this).tooltip('hide');
        }).bind(this), 2000);
    }).on('click', function() {
        $(this).tooltip('show');
    });
});

$('.toggle-btn').on('click', function() {
    get_id_obj($(this).data('target-id')).toggle();
}); 

$('.auto-adjust-height').on('click change keyup keydown paste cut input', function(){
    $(this).height(5);
    $(this).height(this.scrollHeight);
});