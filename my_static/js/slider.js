$(document).ready(function() {
    $('.show-room-slider').slick({
        autoplay: true,//自動的に動き出すか。初期値はfalse。
        infinite: true,//スライドをループさせるかどうか。初期値はtrue。
        speed: 500,//スライドのスピード。初期値は300。
        slidesToScroll: 1,//1回のスクロールで1枚の写真を移動して見せる
        focusOnSelect: true,
        centerMode: true,//要素を中央ぞろえにする
        centerPadding: '10%',
        dots: true,//下部ドットナビゲーションの表示
        arrows: true,
    });
});

function active_slick_room_item(source) {
    source.find('.slider').not('.slick-initialized').slick({
        infinite: true,//スライドをループさせるかどうか。初期値はtrue。
        speed: 500,//スライドのスピード。初期値は300。
        slidesToScroll: 1,//1回のスクロールで1枚の写真を移動して見せる
        focusOnSelect: true,
        centerMode: true,//要素を中央ぞろえにする
        centerPadding: '10%',
        dots: true,//下部ドットナビゲーションの表示
        arrows: true,
    });
}

function active_slick_modal(source) {
    source.find('.slider').not('.slick-initialized').slick({
        autoplay: true,//自動的に動き出すか。初期値はfalse。
        infinite: true,//スライドをループさせるかどうか。初期値はtrue。
        speed: 500,//スライドのスピード。初期値は300
        autoplaySpeed: 1000,
        slidesToScroll: 1,//1回のスクロールで1枚の写真を移動して見せる
        focusOnSelect: true,
        centerMode: true,//要素を中央ぞろえにする
        centerPadding: '10%',
        dots: true,//下部ドットナビゲーションの表示
        arrows: true,
    });
}