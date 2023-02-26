function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function get_dict_value(dict, key) {
    return dict[key] ? dict[key] : '';
}

function is_empty(str) {
    if (str === undefined | str === null) {
        return true;
    }
    if (typeof str == 'string' && str.trim() === "") {
        return true;
    }
    if (str.length === 0) {
        return true;
    }

    return false;
}

function is_same_empty_count(list, allow_empty_count=1) {
    var empty_count = 0

    $.each(list, function(idx, val) {
        empty_count += is_empty(val) ? 1 : 0;
    });

    return empty_count == allow_empty_count ? true : false;
}

function is_str(value) {
    return typeof value == 'string';
}

function is_int(value) {
    if (is_empty(value)) {
        return false;
    }
    if (is_str(value)) {
        value = Number(value.trim());
    }

    return Number.isInteger(value);
}

function show_modal_message(title='', messages=[], footer='') {
    $('#modal-message').find('.modal-title').html(title);
    var message = '';
    $.each(messages, function(index, value) {
        message += `<span>${value}</span><br>`;
    });
    $('#modal-message').find('.modal-body').html(message);
    $('#modal-message').find('.modal-footer').html(
        `${footer}<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>`
    );
    show_modal('modal-message');
}

function get_video_preview_files(name, fd=null) {
    return get_preview_files('video', name, fd);
}

function get_img_preview_files(name, fd=null) {
    return get_preview_files('img', name, fd);
}

function get_preview_files(file_type, name, fd=null) {
    if (is_empty(fd)) {
        var fd = new FormData();
    }
    var preview_items = document.getElementsByClassName(`${name}-${file_type}-preview`);
    if (preview_items.length < 1) {
        return fd;
    }

    var file_names = [];
    var upload_file_names = [];
    $.each(preview_items, function(idx, item) {
        file_names.push(item.getAttribute('file-name'));
        if (item.getAttribute('file-name') != item.getAttribute('id')) {
            upload_file_names.push(item.getAttribute('file-name'));
        }
    });
    fd.append(`${file_type}_file_names`, file_names);

    $.each(upload_file_names, function(idx1, upload_file_name) {
        $(`.${name}-${file_type}-preview-uploader`).each(function() {
            if (this.files.length < 1) {
                return true;
            }
            $.each(this.files, function(idx3, file) {
                if (file.name == upload_file_name) {
                    fd.append(upload_file_name, file);
                    return false;
                }
            });
        });
    });
    
    return fd;
}

function get_file_size_by_unit(byte, unit='MB') {
    unit = unit.toUpperCase();
    if (unit == 'KB') {
        return String(Math.ceil(byte / 1024 * 10) / 10) + unit;
    }
    if (unit == 'MB') {
        return String(Math.ceil(byte / (1024**2) * 10) / 10) + unit;
    }
    if (uint == 'GB') {
        return String(Math.ceil(byte / (1024**3) * 10) / 10) + unit;
    }

    return String(Math.ceil(byte * 10) / 10) + 'B';
}

function set_upload_file_size(name, file_type, size, max_size) {
    var target = $(`#${name}-${file_type}-upload-size`);
    var size = size + parseFloat(target.data('size'));
    target.data('size', size);
    target.text(get_file_size_by_unit(size));

    if (size < max_size) {
        $(`#${name}-${file_type}-size-error`).remove();
        return true;    
    }
    if ($(`#${name}-${file_type}-size-error`).length < 1) {
        target.after(`<span id="${name}-${file_type}-size-error" class="file-size-error error"><br>ファイルサイズを${max_size/1024/1024}MB以下にしてください</span>`)
    }
    return true;
}

function preview_upload(file_type, files, name, max_files=1, max_size=1){
    // file_type in [img, video]
    var ok_files = 0;
    var remaining = max_files - $(`.${name}-${file_type}-preview`).length;
    
    for (var i=0; i < Math.min(files.length, remaining); i++) {
        if (read_file(file_type, name, files[i], $(`.${name}-${file_type}-preview-list`), Math.floor(12 / max_files))) {
            ok_files += 1;
            set_upload_file_size(name, file_type, files[i].size, max_size);
        }
    }
    
    if (ok_files < 1) {
        return false;        
    }
    $(`.${name}-${file_type}-preview-uploader`).hide();

    if (remaining - ok_files > 0) {
        if (file_type == 'img') {
            create_img_input(name);
        } else if (file_type == 'video') {
            create_video_input(name);
        } else {
            console.log("i don't know file type..");
        }
    } else {
        $(`label.${name}-${file_type}-preview-uploaders`).hide();
    }
}

function read_file(file_type, name, file, append_to, col=2) {
    // file_type in [img, video]
    var is_img = file_type == 'img' & file.type.indexOf('image/') != -1;
    var is_video = file_type == 'video' & file.type.indexOf('video/') != -1;
    if (!is_img & !is_video) {
        console.log("i don't know input file...");
        return false;
    }

    var fileReader = new FileReader();
    fileReader.onload = (function (e) {
        if (is_img) {
            append_to.append(get_img_preview_html(e.target.result, name, file.name, file.size, col));
        } else if (is_video) {
            append_to.append(get_video_preview_html(e.target.result, name, file.name, file.size));
        } else {
            return false;
        }
    });
    
    fileReader.readAsDataURL(file);
    return true;
}

function get_img_preview_html(img_path, name, file_name="", file_size=0, col=2, has_delete=true) {
    var html = `<div class="${name}-img-preview col-${col}" file-name="${file_name}" data-size="${file_size}">
        <img src="${img_path}" class="img-fluid corner-circle">`
    if (has_delete) {
        html += `<div class="delete">
            <a class="${name}-img-delete-button delete-font">削除</a>
            </div>`
    }
    html += `</div>`;
    return html;
}

function get_video_preview_html(video_path, name, file_name="", file_size=0, has_delete=true) {
    var html = `<div class="${name}-video-preview" file-name="${file_name}" data-size="${file_size}">
        <video controls src="${video_path}" class="${name}-video"></video>`
    if (has_delete) {
        html += `<div class="delete">
            <a class="${name}-video-delete-button delete-font">削除</a>
        </div>`
    }
    html += `</div>`;
    return html;
}

function delete_img_preview(del_btn, name, max_size, is_multi=true) {
    delete_preview('img', del_btn, name, max_size, is_multi);
}

function delete_video_preview(del_btn, name, max_size, is_multi=true) {
    delete_preview('video', del_btn, name, max_size, is_multi);
}

function delete_preview(type, del_btn, name, max_size, is_multi=true) {
    set_upload_file_size(name, type, -parseFloat(del_btn.parents(`.${name}-${type}-preview`).data('size')), max_size);
    del_btn.parents(`.${name}-${type}-preview`).remove();
    
    $(`.${name}-${type}-preview-uploaders`).show();
    if (!is_multi) {
        $(`.${name}-${type}-preview-uploader`).val(null);
        return true;
    }
    $(`.${name}-${type}-preview-uploader`).hide();
    if (type == 'img') {
        create_img_input(name, is_multi);
    } else if (type == 'video') {
        create_video_input(name, is_multi);
    }
}

//todo 特定のクラスがないと影響が出るのはいかがなものか
function create_img_input(name, is_multi=true) {
    var html = `<input type="file" class="${name}-img-preview-uploader file-uploader" name="img" file-name="" accept="image/*"`;
    if (is_multi) {
        html += ' multiple ';
    }
    html += '>';

    $(`.${name}-img-preview-uploaders`).prepend(html);
}

function create_video_input(name, is_multi=false) {
    var html = `<input type="file" class="form-control ${name}-video-preview-uploader file-uploader" name="video" file-name="" accept="video/*">`;
    $(`.${name}-video-preview-uploaders`).prepend(html);
}

function get_confirm_button(value, add_class='', is_success=true) {
    var html = `<a type="button" role="button" class="btn btn-`;
    if (is_success) {
        html += 'success '
    } else {
        html += 'danger '
    }

    if (add_class != '') {
        html += add_class;
    }

    html += `" data-bs-dismiss="modal">${value}</a>`;

    return html
}

function delete_list_item(list, item) {
    var idx = list.indexOf(item);
    if (idx != -1) {
        list.splice(idx, 1); 
    }
    return list;
}

function search(target) {
    var id = target.data('id');
    var search_word = $('#' + id).val();
    $.ajax({
        url: target.data('action'),
        type:'GET',
        data:{search_word: search_word},
        dataType:'json',
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        $('.search-results').empty();
        if ('rooms' in data) {
            $.each(data.rooms, function(idx, room) {
                $('.search-results').prepend(create_search_room_result(room));
            });
        } else if ('users' in data) {
            $.each(data.users, function(idx, user) {
                $('.search-results').prepend(create_search_user_result(user));
            });
        }

        if ($('.search-results').children().length < 1) {
            $('.search-results').prepend(`<span class="error">現在の検索条件では見つかりません</span>`);
        }
    }).fail(function (data) {
        show_modal_message(data.status, [data.statusText]);
    });
}

function toggle_text(obj, id, checked, unchecked) {
    if (obj.is(':checked')) {
        $('#' + id).text(checked);
    } else {
        $('#' + id).text(unchecked);
    }
}

function toggle_is_public(obj, id) {
    toggle_text(obj, id, '公開', '非公開');
}

function toggle_need_approval(obj, id) {
    toggle_text(obj, id, '必要', '不要');
}

function active_luminous(id) {
    var luminousTrigger = document.querySelectorAll(`.luminous-list-${id}`);
    if( luminousTrigger !== null ) {
        new LuminousGallery(luminousTrigger);
    }
}

function add_class(target, cls) {
    if (is_empty(target)) {
        return false;
    }
    if (!target.hasClass(cls)) {
        target.addClass(cls);
    }
    return true;
}

function remove_class(target, cls) {
    if (is_empty(target)) {
        return false;
    }
    if (target.hasClass(cls)) {
        target.removeClass(cls);
    }
    return true;
}

function form_valid(form_id, show_error_message=false) {
    var form = $(`#${form_id}`);
    form.find('input').each(function(){
        if ($(this).hasClass('validate-length')) {
            validate_length($(this), $(this).val(), $(this).data('min-len'), $(this).data('max-len'));
        }
    });
    var bool = form.valid() & form.find('.error:visible').length < 1;
    if (!bool & show_error_message) {
        show_modal_message('エラー', ['エラーを修正してください']);
    }

    return bool;
}

function error_valid(form_id) {
    return $(`#${form_id}`).find('.error:visible').length < 1;
}

function create_spinner() {
    $('body').append(`
    <div id="overlay">
        <div class="cv-spinner">
            <span class="spinner"></span>
        </div>
    </div>`);
    $('#overlay').fadeIn(300);
}

function remove_spinner() {
    $('#overlay').fadeOut(300);
}

function get_form_input_data(form_id, fd=null) {
    return get_form_data(form_id, ['input'], fd);
}

function get_form_data(form_id, tags=[], fd=null) {
    if (is_empty(fd)) {
        var fd = new FormData();
    }

    $.each(tags, function(idx, tag) {
        $(`#${form_id}`).find(tag).each(function(){
            if (is_empty($(this).attr('name'))) {
                return true;
            }

            var value = '';
            if ($(this).attr('type') == 'checkbox') {
                value = $(this).prop('checked');
            } else {
                value = $(this).val();
            }
            fd.append($(this).attr('name'), value);
        });
    });
    return fd;
}

function adapt_linebreaks(str) {
    return str.replaceAll(/\n/g, '<br>');
}

function get_int(value, defa=0) {
    if (is_int(value)) {
        return parseInt(value.trim());
    }
    return defa;
}

function validate_length(target, text, min_length=0, max_length=255) {
    if (is_validate_length(text, min_length, max_length)) {
        target.parent().find('.length-error').hide();
        return true;
    }
    
    if (target.parent().find('.length-error').length > 0) {
        target.parent().find('.length-error').show();
        return true;
    }

    target.parent().append(`
    <br><span class="error length-error">${get_between_length_message(min_length, max_length)}</span>
    `);
}

function is_validate_length(text, min_length, max_length) {
    if (!is_int(min_length) & !is_int(max_length)) {
        return false;
    }

    text = text.trim();
    if (is_int(min_length) & text.length < parseInt(min_length)) {
        return false;
    }
    if (is_int(max_length) & text.length > parseInt(max_length)) {
        return false;
    }

	return true;
}

function validate_num(target, num, min_length=0, max_length=255) {
    if (is_validate_num(num, min_length, max_length)) {
        target.parent().find('.num-error').hide();
        return true;
    }
    
    if (target.parent().find('.num-error').length > 0) {
        target.parent().find('.num-error').show();
        return true;
    }

    target.parent().append(`
    <br><span class="error num-error">${get_between_length_message(min_length, max_length)}</span>
    `);
}

function is_validate_num(num, min_length, max_length) {
    if (!is_int(min_length) & !is_int(max_length)) {
        return false;
    }
    if (!is_int(num)) {
        return false;
    }

    if (parseInt(num) < parseInt(min_length) | parseInt(num) > parseInt(max_length)) {
        return false;
    }
    return true;
}

function validate_integer(target, text) {
    if (is_int(text)) {
        target.parent().find('.integer-error').hide();
        return true;
    }
    
    if (target.parent().find('.integer-error').length > 0) {
        target.parent().find('.integer-error').show();
        return true;
    }

    target.parent().append(`
        <br><span class="error integer-error">${get_only_integer()}</span>
    `);
}

function show_room_request_information(rris, room_id) {
    var html = '<form id="room-information-form">';
    var form_content = '';
    $.each(rris, function(idx, rri) {
        if (is_empty(rri)) {
            return true;
        }
        if (!rri.is_active) {
            return true;
        }
        form_content += `<div class="form-group"><div class="headline">${escapeHTML(rri.title)}</div>`;
        if (rri.type == 'choice') {
            form_content += get_choice_html(rri.choice, rri.sequence);
        } else if (rri.type == 'char') {
            form_content += get_char_html(rri.min_length, rri.max_length, rri.sequence);
        } else if (rri.type == 'num') {
            form_content += get_num_html(rri.min_length, rri.max_length, rri.sequence);
        }
        form_content += `</div>`;
    });
    if (is_empty(form_content)) {
        return true;
    }
    html += form_content + '</form>';
    $('#modal-room-request-information').find('.modal-title').html('情報要求');
    $('#modal-room-request-information').find('.modal-body').html(html);
    var footer = '<button id="submit-room-information" class="btn btn-secondary btm-sm"';
    if (!is_empty(room_id)) {
        footer += ` data-room-id="${room_id}" `;
    }
    footer += `>送信</button>`;
    $('#modal-room-request-information').find('.modal-footer').html(footer);
    show_modal('modal-room-request-information');
}

function get_choice_html(text, name, divider='&') {
    var choices = text.split(divider);
    var html = `<select name="${name}">`;
    $.each(choices, function(idx, choice) {
        choice = escapeHTML(choice);
        html += `<option value="${choice}">${choice}</option>`
    });
    html += `</select>`;
    return html;
}

function get_char_html(min_length, max_length, name) {
    return `<input type="text" name="${name}" class="validate-length" data-min-len="${min_length}" data-max-len="${max_length}"><div class="char-len c-green"></div>`;
}

function get_num_html(min_length, max_length, name) {
    return `<input type="text" name="${name}" class="validate-length num-autocomplete" data-min-len="${min_length}" data-max-len="${max_length}"><div class="char-len c-green"></div>`;
}

function show_modal(id) {
    var modal = new bootstrap.Modal($(`#${id}`), {});
    modal.show();
}

function close_modal(id) {
    $(`#${id}`).modal('hide');
}

function escapeHTML(string){
    return string.replace(/&/g, '&lt;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, "&#x27;");
}

function append_removable_tag(val, append_to) {
    if (is_empty(val)) {
        return false;
    }
    val = escapeHTML(val);
    if (is_str(append_to)) {
        append_to = $(append_to);
    }
    var input_tags = append_to.siblings('input[name="tags"]');

    if (input_tags.val().split(',').includes(val)) {
        $('.input-tag').val('');
        return false;
    }
    append_to.append(`<div class="removable-tag-item tag-item">${val}</div>`);
    if (input_tags.length < 1) {
        append_to.next(`<input type="hidden" value="${val}" name="tags">`);
        return true;
    }
    var tags = input_tags.val();
    if (tags != '') {
        tags += ',';
    }
    input_tags.val(`${tags}${val}`);
}

function get_option(val) {
    return `<option value="${val}">${val}</option>`;
}