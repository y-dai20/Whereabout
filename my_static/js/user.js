$('#reset-password-btn').on('click', function(){
    var form_id = 'reset-password-form';
    if (!form_valid(form_id)) {
        return false;
    }

    $.ajax({
        url: location.href,
        type:'POST',
        data:get_form_input_data(form_id),
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

$('#signup-btn').on('click', function(){
    var form_id = 'signup-form';
    if (!form_valid(form_id)) {
        return false;
    }

    $.ajax({
        url: location.href,
        type:'POST',
        data:get_form_input_data(form_id),
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

$('#change-password-btn').on('click', function(){
    var form_id = 'change-password-form';
    if (!form_valid(form_id)) {
        return false;
    }

    $.ajax({
        url: $(this).data('url'),
        type:'POST',
        data:get_form_input_data(form_id),
        dataType:false,
        processData:false,
        contentType:false,
        timeout:60000,
    }).done(function (data) {
        var footer = '';
        if (data.is_success) {
            footer = `<a class="btn btn-success" href="${data.url}">ログアウト</a>`;
        }
        show_modal_message(data.title, data.message, footer);
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
});

$('#send-mail-for-signup-btn').on('click', function(){
    var form_id = 'signup-send-mail-form';
    if (!form_valid(form_id)) {
        return false;
    }
    create_spinner();
    $.ajax({
        url:$(this).data('url'),
        type:'POST',
        data:get_form_input_data(form_id),
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

$('#send-mail-for-reset-password-btn').on('click', function(){
    var form_id = 'reset-password-send-mail-form';
    if (!form_valid(form_id)) {
        return false;
    }

    create_spinner();
    $.ajax({
        url: $(this).data('url'),
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