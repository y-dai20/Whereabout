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