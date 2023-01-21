$('#reply-check-input-all').on('change', function(){
    change_children_checkbox('reply-check-input', $(this).prop('checked'));
}); 
$('#post-check-input-all').on('change', function(){
    change_children_checkbox('post-check-input', $(this).prop('checked'));
}); 
$('#admin-check-input-all').on('change', function(){
    change_children_checkbox('admin-check-input', $(this).prop('checked'));
}); 
function change_children_checkbox(cls, is_checked) {
    $(`.${cls}`).each(function(){
        $(this).prop('checked', is_checked);
    });
}

$('.reply-check-input').on('change', function(){
    not_check_parent_checkbox($(this), 'reply-check-input');
});
$('.post-check-input').on('change', function(){
    not_check_parent_checkbox($(this), 'post-check-input');
});
$('.admin-check-input').on('change', function(){
    not_check_parent_checkbox($(this), 'admin-check-input');
});
function not_check_parent_checkbox(target, cls) {
    if (!target.prop('checked')) {
        $(`#${cls}-all`).prop('checked', false);
        return false;
    }
    check_parent_checkbox(cls);
};
function check_parent_checkbox(cls) {
    if($(`.${cls}`).length < 1) {
        return false;
    }
    
    var break_out = false;
    $(`.${cls}`).each(function(){
        if (!$(this).prop('checked')) {
            break_out = true;
            return false;
        }
    });

    if (!break_out) {
        $(`#${cls}-all`).prop('checked', true);
    }
}

$(document).ready(function() {
    check_parent_checkbox('reply-check-input');
    check_parent_checkbox('post-check-input');
    check_parent_checkbox('admin-check-input');
});