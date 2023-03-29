//todo 投稿したら入力内容をクリアにする
$('#submit-post-btn').on('click', function(event) {
    event.preventDefault();
    var form = 'post-form';
    if (!form_valid(form)) {
        return false;
    }
    var fd = get_img_preview_files('post');
    fd = get_video_preview_files('post', fd);
    fd = get_form_data(form, ['input', 'textarea', 'select'], fd);

    $.ajax({
        url:$(this).data('url'),
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