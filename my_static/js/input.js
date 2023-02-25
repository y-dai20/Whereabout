$('.zip-code-input').on('change', function() {
    var val = only_integer($(this).val());
    if (val.length > 2) {
        val = val.slice(0, 3) + '-' + val.slice(3, 7);
    }
    $(this).val(val);
});

$('.num-autocomplete').on('change', function() {
    var val = only_integer($(this).val());
    if (val < $(this).data('min-len')) {
        val = $(this).data('min-len');
    } else if (val > $(this).data('max-len')) {
        val = $(this).data('max-len');
    }
    $(this).val(val);
});

$('.not-w-space').on('change keyup', function() {
    var val = $(this).val().replace(/\s+/g, '');
    $(this).val(val);
});

$('.full-to-half').on('change', function() {
    var val = full_to_half($(this).val());
    $(this).val(val);
});
$('.half-to-full').on('change', function() {
    $(this).val(half_to_full($(this).val()));
});

function full_to_half(val) {
    return val.replace(/[Ａ-Ｚａ-ｚ０-９！”＃＄％＆’（）＝＜＞，．？＿［］｛｝＠＾～￥]/g, function(s) {
        return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);
    }).replace(/[-－﹣−‐⁃‑‒–—﹘―⎯⏤ーｰ─━]/g, '-');
}
function half_to_full(val) {
    return val.replace(/[A-Za-z0-9!"#$%&'()=<>,.?_\[\]{}@^~\\]/g, function(s) {
        return String.fromCharCode(s.charCodeAt(0) + 0xFEE0);
    });
}

function only_integer(val) {
    val = full_to_half(val);
    return val.replace(/[^0-9]/g, '');
}

