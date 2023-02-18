const MAX_ROW = 10;
const MAX_TAB = 10;
const MAX_COLUMN = 12;
const COLUMN = 4;
const COL = MAX_COLUMN / COLUMN;
var ROW = 4;
var now_drag_object = null;
var now_click_object = null;

$(document).ready(function(){
    $('.trash-area').droppable({
        drop: function(){
            repair_expand();
            now_drag_object.remove();
            get_addable_object_list();
        }
    });    
});


function create_room_tab_titles(tab_titles, is_editable=true, active_idx=0) {
    if (tab_titles.length < 1) {
        return true;
    }

    var is_active;
    $.each(tab_titles, function(idx, tab_title) {
        if (is_empty(tab_title) || is_empty(tab_title.title)) {
            return false;
        }
        
        is_active = (idx == active_idx) ? true : false;
        create_room_tab_title(tab_title.id, tab_title.title, is_editable, is_active);
        return true;
    });
}

function create_room_tab_title(id="None" ,title="title", is_editable=true, is_active=false) {
    if (is_empty(id)) {
        id = ' ';
    }
    var tab = $('.room-tab-title').length + 1;
    if (is_editable) {
        var html = `<a id="room-tab-title${tab}" class="room-tab-title nav-link`;
    } else {
        var html = `<a id="room-tab-title${tab}" class="room-tab-title sidebar-button nav-link`;
    }
    if (is_active) {
        $('.room-tab-title').removeClass('active');
        html += ` active `;
    }
    // エラーになる
    // html += `" data-tab="${tab}" data-room-tab-id="${id}" data-bs-toggle="pill" data-bs-target="#room-tab-pane${tab}" type="button" role="pill">`;
    html += `" data-tab="${tab}" data-room-tab-id="${id}" data-bs-toggle="pill" data-bs-target="#room-tab-pane${tab}">`;
    if (is_editable) {
        // html += `<textarea class="input-room-tab-title" id="input-room-tab-title${tab}">${escapeHTML(title)}</textarea>`;
        html += `<input class="input-room-tab-title" id="input-room-tab-title${tab}" value="${escapeHTML(title)}">`;
    } else {
        html += `<h3 class="room-tab-title-font">${escapeHTML(title)}</h3>`;
    }
    html += `</a>`;
    if (is_editable) {
        html += `<div class="delete-tab-button" data-tab="${tab}">
        <img src="${deleteImg}" class="tab-delete-button"></div>`;
    }

    $('.room-tab-title-list').append(html);
}

function create_room_tab_table(tab, is_droppable=true, is_active=false) {
    var html = `
        <div class="tab-pane room-tab-pane`;
    if (is_active) {
        $('.room-tab-pane').removeClass('active');
        html += ' active ';
    }
    html += `" id="room-tab-pane${tab}">
    <div class="container room-tab-table p-0" id="room-tab-table${tab}" data-tab="${tab}">`;

    for (var row = 1; row <= ROW; row++) {
        html += get_room_tab_table_row(tab, row, is_droppable);
    };

    html += `</div></div>`;
    $('#room-tab-pane-list').append(html);
    bind_droppable();
}

function get_room_tab_table_row(tab, row, is_droppable=true) {
    var html = `<div class="row room-tab-table-row">`;
    for (var c = 1; c <= COLUMN; c++) {
        html += `<div id="${get_tab_col_name(tab, row, c)}" class="room-tab-table-col col-3 `;
        if (is_droppable) {
            html += ` border border-white droppable `;
        }

        html += `" data-tab="${tab}" data-row="${row}" data-column="${c}" data-col="3"></div>`;
    };
    html += `</div>`;

    return html;
}

function get_tab_col_name(tab, row, column) {
    return `tab${tab}-row${row}-column${column}`;
}

function get_addable_object_list() {
    now_drag_object = null;
    $('.addable-object-list').html(`
        <div class="my-col">
        <div class="draggable addable-object" id="addable-object-title">
        <img src="${titleImg}" class="image">
        </div>
        </div>
        <div class="my-col">
        <div class="draggable addable-object" id="addable-object-textarea">
        <img src="${textImg}" class="image">
        </div>
        </div>
        <div class="my-col">
        <div class="draggable addable-object" id="addable-object-img">
            <img src="${imageImg}" class="image">
        </div>
        </div>
    `);
    bind_droppable();
}

function expand_object(tab, row, column, fromCol, toCol=-1) {
    if (toCol == -1) {
        toCol = fromCol + COL;
    }

    if (toCol % COL != 0 || ((column - 1) * COL + fromCol >= MAX_COLUMN) || column >= COLUMN) {
        return false;
    }

    if ($('#'+get_tab_col_name(tab, row, column + fromCol/COL)).children('.draggable').length > 0) {
        return false;
    }

    $('#'+get_tab_col_name(tab, row, column)).data('col', toCol);
    $('#'+get_tab_col_name(tab, row, column)).removeClass(`col-${fromCol}`).addClass(`col-${toCol}`);
    var next_column = column + fromCol / COL;
    for (var i=0; i < (toCol - fromCol) / COL; i++) {
        $('#'+get_tab_col_name(tab, row, next_column + i)).hide();
    }
}

function repair_expand(drop_row=0, drop_col=0) {
    var target = now_drag_object.parent();
    var tab = target.data('tab');
    var row = target.data('row');
    var column = target.data('column');
    var col = target.data('col');

    if (col <= COL | (column == drop_col & row == drop_row)) {
        return true;
    }
    $('#'+get_tab_col_name(tab, row, column)).removeClass(`col-${col}`).addClass(`col-3`);
    $('#'+get_tab_col_name(tab, row, column)).data('col', COL);
    for (var i = 1; i < col/COL; i++) {
        $('#'+get_tab_col_name(tab, row, column+i)).show();
    }
}

function bind_droppable() {
    $(".addable-object, .added-object").draggable({
        revert: true,
        start:function() {
            $(this).css('max-width', '50px');
            $(this).css('max-height', '50px');
            $(this).css('z-index', 100);
            now_drag_object = $(this);
        },
        stop: function() {
            $(this).css('max-width', '');
            $(this).css('max-height', '');
            $(this).css('z-index', 10);
            now_drag_object = null;
        },
        cursor:"grab",
        cursorAt:{left: 25, top: 0},
    });

    $(".addable-object, .added-object").on('click', function(){
        now_click_object = $(this);
    });

    $(".droppable.room-tab-table-col").droppable({
        drop: function() {
            var drop_row = $(this).data('row');
            var drop_col = $(this).data('column');

            if($.trim($(this).text()) != '' | now_drag_object == null){
                return false;
            }
            
            $(this).html(get_added_area());
            if(now_drag_object.attr('id') == 'addable-object-title') {
                $(this).children().append(get_title_object());
            } else if(now_drag_object.attr('id') == 'addable-object-textarea') {
                $(this).children().append(get_textarea_object());
            } else if (now_drag_object.attr('id') == 'addable-object-img') {
                $(this).children().append(get_img_object());
            } else {
                $(this).children().append(now_drag_object.children());
                repair_expand(drop_row, drop_col);
            }

            if ($(this).parents('.room-tab-table-row').height() < $(this).height()) {
                $(this).parents('.room-tab-table-row').height($(this).height());
            }
            
            now_click_object = $(this);
            now_drag_object.remove();
            get_addable_object_list();
        }
    });
}

function get_added_area() {
    return `<div class="draggable added-object"></div>`;
}

function get_title_object(text="タイトル") {
    return `<textarea class="added-object-title tab-title-style">${escapeHTML(text)}</textarea>`;
}

function get_textarea_object(text="テキスト") {
    return `<textarea class="added-object-textarea tab-text-font">${escapeHTML(text)}</textarea>`;
}

function get_img_object(file_name='') {
    return `<input type="file" class="custom-file-input room-tab-content-img-preview-uploader added-object-img" name="img" file-name="${file_name}" accept="image/*">
    <div class="room-tab-content-img-preview-list"></div>`;
}

function deploy_tab_content_items(tab, tab_content_items, is_droppable=true) {
    for (var i=0; i < tab_content_items.length; i++) {
        var data = {
            'title':get_dict_value(tab_content_items[i], 'title'),
            'text':get_dict_value(tab_content_items[i], 'text'),
            'img':get_dict_value(tab_content_items[i], 'img'),
        }
        var row = get_dict_value(tab_content_items[i], 'row');
        var column = get_dict_value(tab_content_items[i], 'column');
        var col = get_dict_value(tab_content_items[i], 'col');

        if (col > COL) {
            expand_object(tab, row, column, COL, col);
        }
        
        var row_count = $(`#room-tab-table${tab}`).children('.room-tab-table-row').length;
        if (row > row_count) {
            var get_rows = row - row_count;
            for (var j=0; j < get_rows; j++) {
                $(`#room-tab-table${tab}`).append(get_room_tab_table_row(tab, row, is_droppable));
            }
        }
        if (is_droppable) {
            set_added_object(tab, row, column, data);
        } else {
            set_object(tab, row, column, data);
        }
    }
    bind_droppable();
}

function set_added_object(tab, row, column, data) {
    var drop_area = $('#'+get_tab_col_name(tab, row, column));
    drop_area.html(get_added_area());
    if (data['title'] != '') {
        drop_area.children().append(get_title_object(data['title']));
    } else if (data['text'] != '') {
        drop_area.children().append(get_textarea_object(data['text']));
    } else if (data['img'] != '') {
        drop_area.children().append(get_img_object(data['img']));
        drop_area.find('.room-tab-content-img-preview-uploader').hide();
        drop_area.find('.room-tab-content-img-preview-list').append(get_img_preview_html(`/media/${data['img']}`, 'room-tab-content', data['img'], 0, 12));
    }
}

function set_object(tab, row, column, data) {
    var drop_area = $('#'+get_tab_col_name(tab, row, column));
    if (data.title != '') {
        drop_area.addClass('tab-title-content');
        drop_area.append(`<h3 class="break-word tab-title-style">${escapeHTML(data.title)}</h3>`);
    } else if (escapeHTML(data.text) != '') {
        drop_area.addClass('tab-text-content');
        drop_area.append(`<pre class="break-word tab-text-font">${escapeHTML(data.text)}</pre>`);
    } else if (escapeHTML(data.img) != '') {
        drop_area.append(`<img class="img-fluid corner-circle" src="/media/${escapeHTML(data.img)}">`);
    }
}

$(document).on('click', '.add-row-button', function() {
    var table = $('.room-tab-pane.active').children('.room-tab-table');
    if (table.find('.room-tab-table-row').length >= MAX_ROW) {
        return false;
    }
    table.append(get_room_tab_table_row(table.data('tab'), table.children().length + 1));
    bind_droppable();
});

$(document).on('click', '.expand-object-button', function(){
    if (now_click_object == null) {
        return false;
    }
    var target = now_click_object.parent();
    var row = parseInt(target.data('row'));
    var column = parseInt(target.data('column'));
    var col = parseInt(target.data('col'));
    var tab = parseInt(target.data('tab'));
    
    expand_object(tab, row, column, col);
});

$(document).on('click change keyup keydown paste cut input', '.added-object-textarea, .added-object-title', function(){
    $(this).parents('.room-tab-table-row').height(20);
    $(this).parents('.room-tab-table-row').height(this.scrollHeight + 20);
});

$(document).on('click', '.add-tab-button', function(){
    if ($('.room-tab-title').length >= MAX_TAB) {
        return false;
    }
    create_room_tab_title(id="None" ,title="title", is_editable=true, is_active=true);

    var tab = $('.room-tab-title').length;
    create_room_tab_table(tab, is_droppable=true, is_active=true);
});

$(document).on('click', '.delete-tab-button', function(){
    var tab = $(this).data('tab');
    $(`#room-tab-title${tab}`).addClass('not-display');
    $(`#room-tab-pane${tab}`).fadeOut();
    $(`#room-tab-title${tab}`).fadeOut();
    $(this).fadeOut();
});

$(document).on('change', '.room-tab-content-img-preview-uploader', function() {
    let files = this.files;
    if (read_file('img', 'room-tab-content', files[0], $(this).next('.room-tab-content-img-preview-list'), col=12)) {
        $(this).hide();
    }
});
$(document).on('click', '.room-tab-content-img-delete-button', function(){
    var pre_id = $(this).attr('pre-id');
    if (document.getElementById(pre_id) != null) {
        $('#' + pre_id).parent().prev('.room-tab-content-img-preview-uploader').show();
        document.getElementById(pre_id).remove();
    }
});

$(document).on('click', '.room-tab-title', function(){
    var room_tab_id = $(this).data('room-tab-id');
    if (is_empty(room_tab_id)) {
        return false;
    }

    create_room_tab_link({'id':room_tab_id, 'title':$(this).text()});
    change_room_tab($(this).text());

    var scroll_target = ".room-title";
    var tab = $(this).data('tab');
    if (Object.keys(RoomTabItems).includes(room_tab_id)) {
        if ($('#room-tab-pane-list').hasClass('show-room')) {
            scroll_to(scroll_target);
        }
        return true;
    }

    $.ajax({
        url: `/get/room-tab-items/`,
        type:'POST',
        data:{'room_tab_id':room_tab_id},
        timeout:60000,
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        if ($('#room-tab-pane-list').hasClass('manage-room')) {
            create_room_tab_table(tab, is_droppable=true, is_active=true);
            get_addable_object_list();
            deploy_tab_content_items(tab, data['room_tab_items']);
        } else if ($('#room-tab-pane-list').hasClass('show-room')) {
            create_room_tab_table(tab, is_droppable=false, is_active=true);
            deploy_tab_content_items(tab, data['room_tab_items'], is_droppable=false);
            scroll_to(scroll_target);
        }
        RoomTabItems[room_tab_id] = data['room_tab_items'];
    });
});

function scroll_to(target) {
    $('.show-room-content').animate({
        scrollTop: $(target).offset().top,
    },1000)
}

function create_room_tab_link(room_tab, append_to="#room-tab-link") {
    $(append_to).html(
        `<a href="${room_tab.id}">${room_tab.title}</a>`
    );
}

function change_room_tab(title) {
    if ($('#room-tab-h1-title').length > 0) {
        $('title').html(title);
        $('#room-tab-h1-title').html(title);
    }
}