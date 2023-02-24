$(document).on('change keyup keydown', '.zip-code-input', function() {
    var val = only_integer($(this).val());
    if (val.length > 2) {
        val = val.slice(0, 3) + '-' + val.slice(3, 7);
    }
    $(this).val(val);
});

function only_integer(val) {
    return val.replace(/[^0-9]/g, '');
}