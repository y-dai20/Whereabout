$(document).ready(function(){
    $('.select-post-room').select2({
        dropdownParent: $('#modal-post'),
        language: 'ja',
    });
});

$(function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

//todo まとめない？？
$(document).ready(function() {
    $('.manage-room-img-preview-list').sortable();
    $('.manage-room-img-preview-list').disableSelection();
    toggle_need_approval($('#manage-room-approval'), 'manage-room-approval-label');
    toggle_is_public($('#manage-room-public'), 'manage-room-public-label');
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
            obj.footer.children('.agree-button').removeClass("btn-outline-success").addClass("btn-success");
            obj.footer.children('.disagree-button').removeClass("btn-danger").addClass("btn-outline-danger");
        } else if (!data['is_agree'] & !data['is_deleted']) {
            obj.footer.children('.agree-button').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.disagree-button').removeClass("btn-outline-danger").addClass("btn-danger");
        } else {
            obj.footer.children('.agree-button').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.disagree-button').removeClass("btn-danger").addClass("btn-outline-danger");
        }

        obj.footer.children('.agree-count').text(data['agree_count']);
        obj.footer.children('.disagree-count').text(data['disagree_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
//todo 複製しているなら同期を取るようにする
$(document).on('click', '.agree-button', function(){
    ajax_agree($(this), true);
});
$(document).on('click', '.disagree-button', function(){
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
            obj.footer.children('.good-button').removeClass("btn-outline-success").addClass("btn-success");
            obj.footer.children('.bad-button').removeClass("btn-danger").addClass("btn-outline-danger");
        } else if (!data['is_good'] & !data['is_deleted']) {
            obj.footer.children('.good-button').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.bad-button').removeClass("btn-outline-danger").addClass("btn-danger");
        } else {
            obj.footer.children('.good-button').removeClass("btn-success").addClass("btn-outline-success");
            obj.footer.children('.bad-button').removeClass("btn-danger").addClass("btn-outline-danger");
        }
        obj.footer.children('.good-count').text(data['good_count']);
        obj.footer.children('.bad-count').text(data['bad_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
$(document).on('click', '.good-button', function(){
    ajax_good($(this), true);
});
$(document).on('click', '.bad-button', function(){
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
            obj.footer.children('.demagogy-button').removeClass("btn-outline-dark").addClass("btn-dark");
            obj.footer.children('.disdemagogy-button').removeClass("btn-dark").addClass("btn-outline-dark");
        } else if (!data['is_true'] & !data['is_deleted']) {
            obj.footer.children('.demagogy-button').removeClass("btn-dark").addClass("btn-outline-dark");
            obj.footer.children('.disdemagogy-button').removeClass("btn-outline-dark").addClass("btn-dark");
        } else {
            obj.footer.children('.demagogy-button').removeClass("btn-dark").addClass("btn-outline-dark");
            obj.footer.children('.disdemagogy-button').removeClass("btn-dark").addClass("btn-outline-dark");
        }
        
        obj.footer.children('.true-count').text(data['true_count']);
        obj.footer.children('.false-count').text(data['false_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}
$(document).on('click', '.demagogy-button', function(){
    ajax_demagogy($(this), true);
});
$(document).on('click', '.disdemagogy-button', function(){
    ajax_demagogy($(this), false);
});

$(document).on('click', '.favorite-button', function(){
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
                return e.replace(whiteStarImg, yellowStarImg)
            });
        } else {
            img.attr('src', function(i, e){
                return e.replace(yellowStarImg, whiteStarImg)
            });
        }

        obj.footer.children('.favorite-count').text(data['favorite_count']);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.follow-button', function(){
    var obj = get_item_data($(this));
    var btn = $(this);
    $.ajax({
        url: `/follow/${obj.username}/`,
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

$(document).on('click', '.block-button', function(){
    var obj = get_item_data($(this));
    $.ajax({
        url: `/block/${obj.username}/`,
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

//todo classでいいのか，idに出来るならそうしよう
$('.accept-invite-button').on('click', function(){
    var target = $(this).parents('.table-col');
    $.ajax({
        url: '/accept/invite/' + target.data('room') + '/',
        type:'POST',
        data:{is_accept: $(this).data('is-accept')},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        target.hide();
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('.profile-accept-button').on('click', function(){
    var target = $(this).parents('.table-col');
    $.ajax({
        url: `/accept/${target.data('room')}/${target.data('username')}/`,
        type:'POST',
        data:{is_blocked: $(this).data('is-blocked')},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        target.hide();
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

var RoomUsers = {'banish':[], 'disbanish':[], 'cancel_invite':[], 'accept':[], 'disaccept':[]};
$(document).on('click', '.banish-button', function(){
    var username = $(this).data('username');
    $(this).removeClass('banish-button btn-danger').addClass('disbanish-button btn-success').text('取消');
    $(this).parent().prependTo("#room-user-blocked-list");
    if ($(this).data('org-state') == 'disbanished') {
        RoomUsers['banish'].push(username);
    }
    RoomUsers['disbanish'] = delete_list_item(RoomUsers['disbanish'], username);
});
$(document).on('click', '.disbanish-button', function(){
    var username = $(this).data('username');
    $(this).removeClass('disbanish-button btn-success').addClass('banish-button btn-danger').text('追放');
    $(this).parent().prependTo("#room-user-list");
    if ($(this).data('org-state') == 'banished') {
        RoomUsers['disbanish'].push(username);
    }
    RoomUsers['banish'] = delete_list_item(RoomUsers['banish'], username);
});
$('.cancel-invite-button').on('click', function(){
    var username = $(this).data('username');
    $(this).parent().hide();
    RoomUsers['cancel_invite'].push(username);
});
$(document).on('click', '.manage-room-accept-button', function(){
    var username = $(this).data('username');
    $(this).removeClass('manage-room-accept-button btn-outline-success').addClass('banish-button btn-danger').text('追放');
    $(this).data('org-state', 'disbanished');
    $(this).parent().children('.manage-room-disaccept-button').hide();
    $(this).parent().prependTo("#room-user-list");
    RoomUsers['accept'].push(username);
});
$(document).on('click', '.manage-room-disaccept-button', function(){
    var username = $(this).data('username');
    $(this).removeClass('manage-room-disaccept-button btn-outline-danger').addClass('disbanish-button btn-success').text('取消');
    $(this).data('org-state', 'banished');
    $(this).parent().children('.manage-room-accept-button').hide();
    $(this).parent().prependTo("#room-user-blocked-list");
    RoomUsers['disaccept'].push(username);
});

$('.enter-search').keypress(function(e){
    if (e.keyCode == 13) {
        search($(this).parent().find('.search-button'));
        return false;
    }
});

$('.search-button').on('click', function(){
    search($(this));
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
        url:$(this).data('href'),
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

//todo 投稿したら入力内容をクリアにする
$('#submit-post-button').on('click', function(event) {
    event.preventDefault();
    var form = 'post-form';
    if (!form_valid(form)) {
        return false;
    }
    var fd = get_img_preview_files('post');
    fd = get_video_preview_files('post', fd);
    fd = get_form_data(form, ['input', 'textarea', 'select'], fd);

    $.ajax({
        url:'/post/',
        type:'POST',
        data:fd,
        cache:false,
        processData:false,
        contentType:false,
        enctype:'multipart/form-data',
        timeout:60000,
    }).done(function(data){
        if (is_error(data)) {
            return false;
        }

        close_modal('modal-post');
        show_modal_message(data.title, data.message);
        if (!is_empty(data.post)) {
            var html = get_post_item(data.post, true);
            $('.post-list').prepend(html);
            active_luminous(data.post.obj_id);
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

//todo htmlでscriptを使用する際にエラーになるないようにする（横展開）
$('#submit-create-room-button').on('click', function(event) {
    event.preventDefault();
    var form = 'create-room-form';
    if (!form_valid(form)) {
        return false;
    }

    var fd = get_img_preview_files('create-room');
    fd = get_form_data(form, ['input', 'textarea'], fd);

    $.ajax({
        url:'/create-room/',
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
        create_myroom_dropdown(data.room_id, data.room_title);
        close_modal('modal-create-room');
        var footer = !is_empty(data.room_id) ? `<a href="/room/${data.room_id}/" role="button" class="btn btn-success">移動</a>` : "";
        show_modal_message(data.title, data.message, footer);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('.save-confirm-button').on('click', function(){
    var save_for = $(this).data('save-for');
    show_modal_message('確認', ['保存しますか'], get_confirm_button('保存', `save-${save_for}-button`));
});
$('.cancel-confirm-button').on('click', function(){
    show_modal_message('確認', ['変更内容をキャンセルしますか'], '<a onclick="location.reload()" type="button" class="btn btn-danger" data-bs-dismiss="modal">キャンセル</a>');
});

//todo 複雑すぎない？？
$(document).on('click', '.save-display-button', function(){
    var form = 'manage-room-display-form';
    if (!form_valid(form)) {
        return false;
    };

    var fd = get_img_preview_files('manage-room');
    fd = get_video_preview_files('manage-room', fd);
    fd = get_form_data(form, ['input', 'textarea'], fd);

    var tabs = [];
    var tab;
    var item;
    var is_include_id = false;
    var create_flag;
    var splice;
    for (var i=1; i <= document.getElementsByClassName('input-room-tab-title').length; i++) {
        if ($(`#room-tab-title${i}`).hasClass('not-display')) {
            continue;
        }
        tab = {
            'content_id':$(`#input-room-tab-title${i}`).parents('.room-tab-title').data('content-id'), 
            'title':document.getElementById(`input-room-tab-title${i}`).value, 
            'content':{'create':[], 'delete':[]}};
        is_include_id = Object.keys(RoomTabItems).includes(tab['content_id']);
        $(`#room-tab-table${i}`).find(`.added-object`).each(function() {
            item = {
                'title':$.trim($(this).find('.added-object-title').val()),
                'text':$.trim($(this).find('.added-object-textarea').val()),
                'img':'',
                'row':$(this).parent().data('row'),
                'column':$(this).parent().data('column'),
                'col':$(this).parent().data('col'),
            }

            $(this).children('.added-object-img').each(function() {
                if ($(this).attr('file-name') != '') {
                    item['img'] = $(this).attr('file-name');
                }

                if (($(this).prop('files')).length > 0) {
                    item['img'] = $(this).prop('files')[0].name;
                    fd.append(item['img'], $(this).prop('files')[0]);
                }
            });
            
            if (!is_include_id || is_empty(tab['content_id'])) {
                tab['content']['create'].push(item);
                return false;
            }

            create_flag = true;
            splice = -1;
            $.each(RoomTabItems[tab['content_id']], function(idx, dict){
                if (dict.row == item.row & dict.column == item.column) {
                    splice = idx;
                    if (dict.col == item.col & dict.title == item.title & dict.text == item.text & dict.img == item.img) {
                        create_flag = false;
                    }
                    return false;
                }
            });
            
            if (splice != -1) {
                RoomTabItems[tab['content_id']].splice(splice, 1);
            }
            
            if (create_flag) {
                tab['content']['create'].push(item);
            }
        });

        tab['content']['delete'] = RoomTabItems[tab['content_id']];
        tabs.push(tab);
    }
    fd.append('tabs', JSON.stringify(tabs));

    $.ajax({
        url:'/manage/room-display/' + $('#manage-room-id').val() + '/',
        type:'POST',
        data:fd,
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

//todo fdを使わない理由は？
$(document).on('click', '.save-participant-button', function(){
    var data = {
        'need_approval':$('#manage-room-approval').is(':checked'),
        'accept_users':RoomUsers['accept'],
        'disaccept_users':RoomUsers['disaccept'],
        'cancel_invite_users':RoomUsers['cancel_invite'],
        'banish_users':RoomUsers['banish'].concat( RoomUsers['disbanish']),
    }

    $.ajax({
        url:'/manage/room-participant/' + $('#manage-room-id').val() + '/',
        type:'POST',
        data:JSON.stringify(data),
        dataType:'json',
        contentType:'application/json; charset=utf-8',
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.save-reply-type-button', function(){
    $.ajax({
        url:'/manage/room-reply-type/' + $('#manage-room-id').val() + '/',
        type:'POST',
        data:get_form_input_data('manage-reply-types-form'),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.save-information-button', function(){
    var room_id = $('#manage-room-id').val();
    var ajax_list = [];
    var ajax_obj;
    var data_list = [];

    $('.manage-information-form').each(function(idx){
        if (!error_valid($(this).attr('id'))) {
            return false;
        }
        var fd = get_form_data($(this).attr('id'), ['input', 'select']);
        fd.append('sequence', idx+1);
        ajax_obj = $.ajax({
            url:`/manage/room-information/${room_id}/`,
            type:'POST',
            data:fd,
            dataType:false,
            processData:false,
            contentType:false,
            timeout:60000,
        }).done(function(data) {
            data_list.push(data);
        }).fail(function(data){
            data_list.push(data);
        });
        ajax_list.push(ajax_obj);
    });

    if (ajax_list.length < 1) {
        return false;
    }
    $.when.apply($, ajax_list).done(function(data) {
        show_modal_message(data[0].title, data[0].message);
        close_modal('modal-message');
    }).fail(function(data) {
        show_modal_message(data[0].status, [data[0].statusText]);
    });
});

$(document).on('click', '.save-authority-button', function(){
    var data = {'checks':[], 'defa':{}};
    $('.authority-user-col').each(function(){
        var reply_check = $(this).find('.reply-check-input');
        var post_check = $(this).find('.post-check-input');
        var admin_check = $(this).find('.admin-check-input');
        if (check(reply_check) | check(post_check) | check(admin_check)) {
            data['checks'].push({
                'username':$(this).data('username'),
                'can_reply':reply_check.prop('checked'),
                'can_post':post_check.prop('checked'),
                'is_admin':admin_check.prop('checked'),
            });    
        }
    });

    if (check($('#defa-reply-check-input')) | check($('#defa-post-check-input')) | check($('#defa-admin-check-input'))) {
        data['defa'] = {
            'can_reply':$('#defa-reply-check-input').prop('checked'), 
            'can_post':$('#defa-post-check-input').prop('checked'), 
            'is_admin':$('#defa-admin-check-input').prop('checked')
        }
    }

    function check(item) {
        var defa = item.data('default');
        return (defa == 'checked' & !item.prop('checked')) | (defa == "" & item.prop('checked'));
    };

    $.ajax({
        url:'/manage/room-authority/' + $('#manage-room-id').val() + '/',
        type:'POST',
        data:JSON.stringify(data),
        dataType:'json',
        contentType:'application/json; charset=utf-8',
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#input-create-room-public').on('click', function() {
    toggle_is_public($(this), 'SwitchIsPublicLabel');
});

$('#manage-room-public').on('click', function(){
    toggle_is_public($(this), 'manage-room-public-label');
});

$('#input-create-room-approval').on('click', function() {
    toggle_need_approval($(this), 'SwitchNeedApprovalLabel');
});

$('#manage-room-approval').on('click', function() {
    toggle_need_approval($(this), 'manage-room-approval-label');
});

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
$(document).on('change', '.create-room-img-preview-uploader', function() {
    preview_upload('img', this.files, 'create-room', MAX_ROOM_IMGS, MAX_ROOM_IMG_BYTE);
});
$(document).on('click', '.create-room-img-delete-button', function(){
    delete_img_preview($(this), 'create-room', MAX_ROOM_IMG_BYTE);
});
$(document).on('change', '.manage-room-img-preview-uploader', function() {
    preview_upload('img', this.files, 'manage-room', MAX_ROOM_IMGS, MAX_ROOM_IMG_BYTE);
});
$(document).on('click', '.manage-room-img-delete-button', function(){
    delete_img_preview($(this), 'manage-room', MAX_ROOM_IMG_BYTE);
});
$(document).on('change', '.manage-room-video-preview-uploader', function() {
    preview_upload('video', this.files, 'manage-room', MAX_ROOM_VIDEOS, MAX_ROOM_VIDEO_BYTE);
});
$(document).on('click', '.manage-room-video-delete-button', function(){
    delete_video_preview($(this), 'manage-room', MAX_ROOM_VIDEO_BYTE);
});
$(document).on('change', '.reply-img-preview-uploader', function() {
    preview_upload('img', this.files, 'reply', MAX_REPLY_IMGS, MAX_REPLY_IMG_BYTE);
});
$(document).on('click', '.reply-img-delete-button', function(){
    delete_img_preview($(this), 'reply', MAX_REPLY_IMG_BYTE, false);
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
        deleteObject.hide();
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

//todo 何に使ってる？
$('.input-tab-content').on('input', function(){
    $(this).height(0).innerHeight(this.scrollHeight);
});

// $("#move-img-dialog").dialog({ autoOpen: false });
// $('.manage-room-img-preview').on('click', function(){
//     // create_dialog('', '', '');
//     $('#move-img-dialog').dialog('open');
// })

// function create_dialog(id, title, text) {
//     document.append(`<div id="move-img-dialog" class="dialog">
//     <div class="title-dialog"></div>
//     <div class="text-dialog">画像をドラッグ＆ドロップで移動できます．</div>
// </div>`)
// }

$(document).on('click', '.invite-user', function() {
    var data = {'username':$(this).data('username')};
    
    $.ajax({
        url:'/invite/room/' + $('#manage-room-id').val() + '/',
        type:'POST',
        data:JSON.stringify(data),
        dataType:'json',
        contentType:'application/json; charset=utf-8',
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('click', '.leave-room-confirm-button', function(){
    var url = $(this).data('url');
    var footer = `<a type="button" role="button" class="leave-room-button btn btn-danger" href="${url}">退出</a>`;
    show_modal_message('確認', ['退出しますか'], footer);
});

//todo urlって何
$(document).on('click', '.join-room-button', function(){
    var url = $(this).data('url');
    var target = $(this);
    $.ajax({
        url:url,
        type:'GET',
        timeout:60000,
    }).done(function(data){
        show_modal_message(data.title, data.message);
        if (!data.is_success) {
            return false;
        }
        target.removeClass('join-room-button');
        if (data.is_waiting) {
            target.prop('disabled', true);
            target.text("許可待ち");
        } else {
            target.addClass('leave-room-confirm-button');
            target.data('url', url.replace('join', 'leave'));
            target.text("退出する");
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#room-video-close-button').on('click', function(){
    $(this).parent().addClass('not-scroll-function');
    $('.room-file-content').css('height', 'auto');
    $('#room-video-area').removeClass('fixed-right-bottom');
    $('#room-video-area').find('.close-button').addClass('not-display');
    $('#room-video-area').css('width', '100%');
});

$('.show-room-content').on('scroll', function(){
    if (!$('video').hasClass('room-video') | $('#room-video-area').hasClass('not-scroll-function')) {
        return false;
    }
    var windowScrollTop = $('body').scrollTop();
    var offsetTop = $('#room-tab-pane-list').offset().top;
    if (windowScrollTop > offsetTop - 50 && !$('#room-video-area').hasClass('fixed-right-bottom')) {
        $('.room-file-content').css('height', $('#room-video-area').height());
        $('#room-video-area').addClass('fixed-right-bottom');
        $('#room-video-area').find('.close-button').removeClass('not-display');
        $('#room-video-area').css('width', '300px');
    } else if (windowScrollTop < offsetTop - 100 && $('#room-video-area').hasClass('fixed-right-bottom')) {
        $('.room-file-content').css('height', 'auto');
        $('#room-video-area').removeClass('fixed-right-bottom');
        $('#room-video-area').find('.close-button').addClass('not-display');
        $('#room-video-area').css('width', '100%');
    }
});

$('#change-video-img-button').on('click', function(){
    if($('#room-img-area').hasClass('not-display')) {
        $('#room-img-area').removeClass('not-display');
        $('#room-video-area').addClass('not-display');
    } else if ($('#room-video-area').hasClass('not-display')) {
        $('#room-img-area').addClass('not-display');
        $('#room-video-area').removeClass('not-display');
    }
});

$(document).on('click', '.save-user-button', function() {
    var form = 'manage-user-form';
    if (!form_valid(form)) {
        return false;
    }
    var fd = get_form_data(form, ['input', 'textarea']);
    fd = get_img_preview_files('user-img', fd);

    $.ajax({
        url:'/profile/',
        type:'POST',
        data:fd,
        dataType:false,
        processData:false,
        contentType:false,
        enctype:'multipart/form-data',
        timeout:60000,
    }).done(function(data){
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
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
            active_slick_room_item();
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

$(document).on('click', '.get-reply-link', function() {
    var obj = get_item_data($(this));
    if ($('.post-detail-link').data('obj-id') == obj.id) {
        return false;
    }

    close_sidebar();
    $('.index-post-reply-sidebar').removeClass('not-display');
    add_class($('.index-post-reply2-sidebar'), 'not-display');

    $('.reply-list').html($(this).clone());
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

$(document).on('click', '.get-reply2-link', function() {
    var obj = get_item_data($(this));
    if ($('.reply-detail-link').data('obj-id') == obj.id) {
        return false;
    }

    $('.index-post-reply2-sidebar').removeClass('not-display');
    $('.reply2-list').html($(this).clone());
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

$('.sidebar-menu').click(function(e) {
    e.stopPropagation();
    var target = $(this).data('for');
    $(this).toggleClass('open');
    $(`.${target}`).toggleClass('not-display');

    $(this).siblings('.sidebar-menu').each(function() {
        var target = $(this).data('for');
        add_class($(`.${target}`), 'not-display');
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

$(document).on('click', '.new-window-open', function() {
    window.open(BASE_URL + $(this).data('href'), '_blank')
});

$('.input-clear-btn').on('click', function(){
    $(this).parents('form').find('input[type="text"]').each(function(){
        $(this).val('');
    });
});

$('#send-mail-for-signup-button').on('click', function(){
    var form = 'signup-send-mail-form';
    if (!form_valid(form)) {
        return false;
    }
    create_spinner();
    $.ajax({
        url:`/signup/`,
        type:'POST',
        data:get_form_input_data(form),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
    remove_spinner();
});

$('#send-mail-for-reset-password-button').on('click', function(){
    var form = 'reset-password-send-mail-form';
    if (!form_valid(form)) {
        return false;
    }

    create_spinner();
    $.ajax({
        url: `/reset-password/`,
        type:'POST',
        data:get_form_input_data(form),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
    remove_spinner();
});

$('#change-password-button').on('click', function(){
    var form = 'change-password-form';
    if (!form_valid(form)) {
        return false;
    }

    $.ajax({
        url: `/change-password/`,
        type:'POST',
        data:get_form_input_data(form),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        var footer = '';
        if (data.is_success) {
            footer = `<a class="btn btn-success" href="/logout/">ログアウト</a>`;
        }
        show_modal_message(data.title, data.message, footer);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#signup-button').on('click', function(){
    var form = 'signup-form';
    if (!form_valid(form)) {
        return false;
    }

    $.ajax({
        url: location.href,
        type:'POST',
        data:get_form_input_data(form),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        if (data.is_success) {
            window.location.href = '/';
        }
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#reset-password-button').on('click', function(){
    var form = 'reset-password-form';
    if (!form_valid(form)) {
        return false;
    }

    $.ajax({
        url: location.href,
        type:'POST',
        data:get_form_input_data(form),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$(document).on('change', '.validate-length', function() {
    validate_length($(this), $(this).val(), $(this).data('min-length'), $(this).data('max-length'));
});
$(document).on('change', '.validate-num', function() {
    validate_num($(this), $(this).val(), $(this).data('min-length'), $(this).data('max-length'));
});
$(document).on('change', '.validate-integer', function() {
    validate_integer($(this), $(this).val());
});

$('#room-request-information-demo-button').on('click', function(){
    var room_id = $('#manage-room-id').val();
    $.ajax({
        url: `/get/room-request-information/${room_id}/`,
        type:'POST',
        timeout:60000,
    }).done(function (data) {
        var rris = data.rri;
        show_room_request_information(rris, '');
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('.request-information-type').on('change', function() {
    var target = $(this).parents('tr').find('.request-information-choice');
    if ($(this).val() == 'choice') {
        target.removeClass('not-display');
        return true;
    }
    add_class(target, 'not-display');
});

$(document).on('click', '#submit-room-information', function(){
    if (!form_valid('room-information-form')) {
        return false;
    }

    var room_id = $(this).data('room-id');
    if (is_empty(room_id)) {
        return false;
    }

    $.ajax({
        url: `/room/information/${room_id}/`,
        type:'POST',
        data:get_form_data('room-information-form', ['input', 'select']),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        close_modal('modal-room-request-information');
        show_modal_message(data.title, data.message);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
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
