//追加個数の制限を設ける
var modalRoomLinkIcon = null;
$(document).on('click', '.select-icon-btn', function() {
    show_modal('modal-room-icon');
    modalRoomLinkIcon = $(this);
});

$(document).on('click', '.delete-room-link-item', function() {
    var id = $(this).parent('.room-link-item').data('id');
    if (!is_empty(id)) {
        deleteRoomLinkIds.push(id);
    }
    $(this).parent('.room-link-item').remove();
});

$('.select-link-item-icon').on('click', function() {
    if (is_empty(modalRoomLinkIcon)) {
        return false;
    }

    modalRoomLinkIcon.html($(this).clone());
    modalRoomLinkIcon = null;
    close_modal('modal-room-icon');
});

$('.add-room-link-btn').on('click', function() {
    $('.room-link-item-list').append(get_editable_room_icon());
});

$('#delete-room-button').on('click', function() {
    var footer = get_delete_btn($(this).data('url'));
    show_modal_message('確認', ['削除しますか'], footer);
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

$('.request-information-type').on('change', function() {
    var target = $(this).parents('tr').find('.request-information-choice');
    if ($(this).val() == 'choice') {
        target.removeClass('not-display');
        return true;
    }
    add_class(target, 'not-display');
});

$('#room-request-information-demo-btn').on('click', function(){
    $.ajax({
        url: $(this).data('url'),
        type:'POST',
        timeout:60000,
    }).done(function (data) {
        var rris = data.rri;
        show_room_request_information(rris, '');
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#change-video-img-button').on('click', function(){
    if($('.show-room-slider').hasClass('not-display')) {
        $('.show-room-slider').removeClass('not-display');
        $('#room-video-area').addClass('not-display');
    } else if ($('#room-video-area').hasClass('not-display')) {
        $('.show-room-slider').addClass('not-display');
        $('#room-video-area').removeClass('not-display');
    }
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
        url:$(this).data('url'),
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

$(document).on('click', '.save-room-personal-button', function(){
    var form = 'manage-room-personal-form';
    if (!form_valid(form)) {
        return false;
    };

    var fd = get_form_data(form, ['input']);
    $.ajax({
        url:'/manage/room-personal/' + $('#manage-room-id').val() + '/',
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

$(document).on('click change input', 'input.input-room-tab-title', function() {
    set_char_len(
        target=$(this).parents('.room-tab-title-list').find(`#room-tab-title${$(this).parents('.room-tab-title').data('tab')}-info`).find('.char-len'), 
        len=$(this).val().length, 
        max_len=ROOM_TAB_TITLE_MAX_LENGTH
    );
});

$(document).on('click change input', 'textarea.added-object-title', function() {
    set_char_len(
        target=$(this).parents('.added-object').find('.char-len'), 
        len=$(this).val().length, 
        max_len=ROOM_TAB_ITEM_TITLE_MAX_LENGTH
    );
});

$(document).on('click change input', 'textarea.added-object-text', function() {
    set_char_len(
        target=$(this).parents('.added-object').find('.char-len'), 
        len=$(this).val().length, 
        max_len=ROOM_TAB_ITEM_TEXT_MAX_LENGTH
    );
});


$(document).on('click', '.save-display-button', function(){
    var form = 'manage-room-display-form';
    if (!form_valid(form)) {
        return false;
    };

    var fd = get_img_preview_files('manage-room');
    fd = get_video_preview_files('manage-room', fd);
    fd = get_form_data(form, ['input', 'textarea'], fd);    
    
    var links = {'create':[], 'update':[], 'delete':deleteRoomLinkIds};
    get_id_obj(form).find('.room-link-item').each(function() {
        var id = $(this).data('id');
        var link = {'id':id, 'icon':$(this).find('img').attr('src'),'link':$(this).find('input').val()};
        if (is_empty(id)) {
            links['create'].push(link);
            return true;
        }
        links['update'].push(link);
    });
    fd.append('links', JSON.stringify(links));

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

$(document).on('click', '.save-tab-button', function() {
    var fd = new FormData();
    var tabs = [];
    var create_flag;
    for (var i=1; i <= $('.input-room-tab-title').length; i++) {
        if ($(`#room-tab-title${i}`).hasClass('not-display')) {
            continue;
        }

        var tab = {
            'room_tab_id':$(`#input-room-tab-title${i}`).parents('.room-tab-title').data('room-tab-id'), 
            'title':$(`#input-room-tab-title${i}`).val(), 
            'items':{'create':[], 'delete':[]}
        };
        var is_include_id = Object.keys(RoomTabItems).includes(tab['room_tab_id']);
        $(`#room-tab-table${i}`).find(`.added-object`).each(function() {
            var item = {
                'title':$(this).find('.added-object-title').val(),
                'text':$(this).find('.added-object-text').val(),
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

            if (!is_same_empty_count([item.title, item.text, item.img], 2)) {
                return true;
            }
            
            if (!is_include_id) {
                tab['items']['create'].push(item);
                return true;
            }

            create_flag = true;
            $.each(RoomTabItems[tab['room_tab_id']], function(idx, dict) {
                if (dict.row == item.row & dict.column == item.column) {
                    RoomTabItems[tab['room_tab_id']].splice(idx, 1);
                    if (dict.col == item.col & dict.title == item.title & dict.text == item.text & dict.img == item.img) {
                        create_flag = false;
                    }
                    return false;
                }
            });
        
            if (create_flag) {
                tab['items']['create'].push(item);
            }
        });
        
        if (is_include_id) {
            tab['items']['delete'] = RoomTabItems[tab['room_tab_id']];
        }
        tabs.push(tab);
    }
    fd.append('tabs', JSON.stringify(tabs));

    $.ajax({
        url:'/manage/room-tab/' + $('#manage-room-id').val() + '/',
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


//todo htmlでscriptを使用する際にエラーになるないようにする（横展開）
$('#submit-create-room-btn').on('click', function(event) {
    event.preventDefault();
    var form = 'create-room-form';
    if (!form_valid(form)) {
        return false;
    }

    var fd = get_img_preview_files('create-room');
    fd = get_form_data(form, ['input', 'textarea'], fd);

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
        create_myroom_dropdown(data.room_id, data.room_title);
        close_modal('modal-create-room');
        //todo url
        var footer = !is_empty(data.room_id) ? `<a href="/room/${data.room_id}/" role="button" class="btn btn-success">移動</a>` : "";
        show_modal_message(data.title, data.message, footer);
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

$('.accept-room-invite-btn').on('click', function(){
    var target = $(this).parents('.table-col');
    $.ajax({
        url: $(this).data('url'),
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

$('.accept-room-guest-btn').on('click', function(){
    var target = $(this).parents('.table-col');
    $.ajax({
        url: $(this).data('url'),
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