$(document).ready(function(){
    active_search_list('search-room-guest');
    active_search_list('search-room-invite-user');
    active_search_list('search-room-block-user');
    active_search_list('search-room-user');
    active_search_input('search-authority-user');
    active_search_input('search-applied-room');
    active_search_input('search-applied-room-user');
    active_search_input('search-invited-room');
    active_search_input('search-invited-room-user');
    active_search_input('search-information-user');
    active_search_input('search-information-1');
    active_search_input('search-information-2');
    active_search_input('search-information-3');
    active_search_input('search-information-4');
    active_search_input('search-information-5');
    active_search_input('search-information-6');
    active_search_input('search-information-7');
    active_search_input('search-information-8');
    active_search_input('search-information-9');
    active_search_input('search-information-10');
    active_search_select('select-reply-check-display');
    active_search_select('select-post-check-display');
    active_search_select('select-admin-check-display');
});

function active_search_list(input_id) {
    var target_cls = input_id.replace("search-", "");
    $(`#${input_id}`).on("keyup", function(){
        var value = $(this).val().toLowerCase();
        $(`#${target_cls}-list > .${target_cls}`).filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
}

function active_search_input(input_id) {
    var target = $(`#${input_id}`);
    target.on('keyup change', function(){
        var value = $(this).val().toLowerCase();
        target.parents('table').find(`tbody tr`).filter(function() {
            var filter = target.data('filter');
            if ($(this).find(`.${filter}`).text().toLowerCase().indexOf(value) > -1) {
                $(this).removeClass(`active-${filter}`);
            } else {
                $(this).addClass(`active-${filter}`);
            }
        });
    });
}
function active_search_select(select_id) {
    var target = $(`#${select_id}`);
    target.on('change', function(){
        var value = $(this).val().toLowerCase();
        target.parents('table').find(`tbody tr`).filter(function() {
            var filter = target.data('filter');

            if ((value == 'checked' & $(this).find(`.${filter}`).prop('checked')) | 
                (value == 'unchecked' & !$(this).find(`.${filter}`).prop('checked')) |
                value == 'all') {
                $(this).removeClass(`active-${filter}`);
            } else {
                $(this).addClass(`active-${filter}`);
            }
        });
    });
}

$('.search-post-button').on('click', function() {
    var url = get_form_href('search-post-form');
    search_post_ajax(url);
});

$('.search-pir-button').on('click', function() {
    var url = get_form_href('search-pir-form');
    search_post_ajax(url);
});

$('.search-user-button').on('click', function() {
    var url = get_form_href('search-user-form');
    search_user_ajax(url);
});

$('.search-room-button').on('click', function() {
    var url = get_form_href('search-room-form');
    search_room_ajax(url);
});

$('.search-reply-button').on('click', function() {
    var url = get_form_href('search-reply-form');
    search_reply_ajax(url);
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