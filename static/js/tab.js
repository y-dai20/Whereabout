const MAX_ROW = 10;
const MAX_TAB = 10;
const MAX_COLUMN = 12;
const COLUMN = 4;
const COL = MAX_COLUMN / COLUMN;
var ROW = 4;
var now_drag_object = null;
var now_click_object = null;

function create_room_tab_titles(tab_contents, is_editable=true) {
    var tab_content = tab_contents.shift(); 
    create_room_tab_title(tab_content.id, tab_content.title, is_editable, is_active=true);
    
    tab_contents.every(function(tab_content) {
        if (is_empty(tab_content) || is_empty(tab_content.title)) {
            return false;
        }
        
        create_room_tab_title(tab_content.id, tab_content.title, is_editable);
        return true;
    });
}

function create_room_tab_title(id="None" ,title="title", is_editable=true, is_active=false) {
    var tab = $('.room-tab-title').length + 1;
    if (is_editable) {
        var html = `<a id="room-tab-title${tab}" class="room-tab-title nav-link`;
    } else {
        var html = `<a id="room-tab-title${tab}" class="room-tab-title sidebar-button nav-link`;
    }
    if (is_active) {
        $('.room-tab-title').removeClass('active');
        html += ` active`;
    }
    html += `" data-tab="${tab}" data-content-id="${id}" data-bs-toggle="pill" data-bs-target="#room-tab-pane${tab}" type="button" role="pill">`;
    if (is_editable) {
        // html += `<textarea class="input-room-tab-title" id="input-room-tab-title${tab}">${title}</textarea>`;
        html += `<input class="input-room-tab-title" id="input-room-tab-title${tab}" value="${title}">`;
    } else {
        html += `${title}`;
    }
    html += `</a>`;
    if (is_editable) {
        html += `<div class="delete-tab-button" data-tab="${tab}">
        <img src="${delete_img}" class="tab-delete-button"></div>`;
    }
    // html += `</div>`;
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
        <div class="draggable addable-object" id="addable-object-title">
            <p>title</p>
        </div>
        <div class="draggable addable-object" id="addable-object-textarea">
            <p>textarea</p>
        </div>
        <div class="draggable addable-object" id="addable-object-img">
            <p>image</p>
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
            now_drag_object = $(this);
        },
        stop: function() {
            $(this).css('max-width', '100%');
            $(this).css('max-height', '100%');
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
    return `<textarea class="added-object-title tab-title-style">${text}</textarea>`;
}

function get_textarea_object(text="テキスト") {
    return `<textarea class="added-object-textarea tab-text-font">${text}</textarea>`;
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
    if (data['title'] != '') {
        drop_area.addClass('tab-title-content');
        drop_area.append(`<span class="break-word tab-title-style">${data['title']}</span>`);
    } else if (data['text'] != '') {
        drop_area.addClass('tab-text-content');
        drop_area.append(`<pre class="break-word tab-text-font">${data['text']}</pre>`);
    } else if (data['img'] != '') {
        drop_area.append(`<img class="img-fluid" src="/media/${data['img']}">`);
    }
}

$('.add-row-button').on('click', function() {
    var table = $('.room-tab-pane.active').children('.room-tab-table');
    if (table.find('.room-tab-table-row').length >= MAX_ROW) {
        return false;
    }
    table.append(get_room_tab_table_row(table.data('tab'), table.children().length + 1));
    bind_droppable();
});

$(".trash-area").droppable({
    drop: function(){
        repair_expand();
        now_drag_object.remove();
        get_addable_object_list();
    }
});

$(".expand-object-button").on('click', function(){
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
    $(this).parents('.room-tab-table-row').height('10px');
    $(this).parents('.room-tab-table-row').height(this.scrollHeight + 15);
});

$('.add-tab-button').on('click', function(){
    if ($('.room-tab-title').length >= MAX_TAB) {
        return false;
    }
    create_room_tab_title(id="None" ,title="title", is_editable=true, is_active=true);

    var tab = $('.room-tab-title').length;
    create_room_tab_table(tab, is_droppable=true, is_active=true);
});

$(document).on('click', '.delete-tab-button', function(){
    var tab = $(this).data('tab');
    $(`#room-tab-title${tab}`).addClass('display-none');
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
    var content_id = $(this).data('content-id');
    var scroll_target = ".room-file-content";
    var tab = $(this).data('tab');
    if (ShowContentIds.includes(content_id)) {
        if ($('#room-tab-pane-list').hasClass('show-room')) {
            scroll_to(scroll_target);
        }
        return true;
    }

    $.ajax({
        url: `/get/tab-contents/`,
        type:'POST',
        data:{'content_id':content_id},
    }).done(function (data) {
        if (is_error(data)) {
            return false;
        }
        if ($('#room-tab-pane-list').hasClass('manage-room')) {
            create_room_tab_table(tab, is_droppable=true, is_active=true);
            get_addable_object_list();
            deploy_tab_content_items(tab, data['content_items']);
        } else if ($('#room-tab-pane-list').hasClass('show-room')) {
            scroll_to(scroll_target);
            create_room_tab_table(tab, is_droppable=false, is_active=true);
            deploy_tab_content_items(tab, data['content_items'], is_droppable=false);
        }
        TabContentItems.push(data['content_items']);
        ShowContentIds.push(content_id);
    });
});

function scroll_to(target) {
    $('.show-room-content').animate({
        scrollTop: $(target).offset().top,
    },1000)
}

$(document).ready(function(){
    if ($('#room-tab-pane-list').hasClass('manage-room')) {
        create_room_tab_titles(TabContents[0], true);
        create_room_tab_table(tab=1, is_droppable=true, is_active=true);
        get_addable_object_list();
        deploy_tab_content_items(tab=1, TabContentItems[0]);
    } else if ($('#room-tab-pane-list').hasClass('show-room')) {
        create_room_tab_titles(TabContents[0], false);
        create_room_tab_table(tab=1, is_droppable=false, is_active=true);
        deploy_tab_content_items(tab=1, TabContentItems[0], is_droppable=false);
    }
});