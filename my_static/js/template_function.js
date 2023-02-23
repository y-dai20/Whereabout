function get_parsed_str(value) {
    if (is_str(value)) {
        value = JSON.parse(value);
    }
    return value;
}

function create_post_items(appendTo, posts, is_link=false) {
    posts = get_parsed_str(posts);
    $.each(posts, function(idx, post) {
        var html = get_post_item(post, is_link);
        $(appendTo).append(html);
        active_luminous(post.obj_id);
    });
}

function create_reply_items(appendTo, replies, is_link=false) {
    replies = get_parsed_str(replies);
    $.each(replies, function(idx, reply) {
        var html = get_reply_item(reply, is_link);
        $(appendTo).append(html);
        active_luminous(reply.obj_id);
    });
}

function create_post_detail_items(appendTo, replies, is_link=false) {
    replies = get_parsed_str(replies);
    $.each(replies, function(idx, reply) {
        var html = `<div class="reply-item-col">` + get_reply_item(reply, is_link) + `</div>`;
        $(appendTo).append(html);
        if (!is_empty(reply)) {
            active_luminous(reply.obj_id);
        }
    });
}

function create_room_items(appendTo, rooms) {
    rooms = get_parsed_str(rooms);
    $.each(rooms, function(idx, room) {
        var html = get_room_item(room);
        $(appendTo).append(html);
        active_slick_room_item($('.room-item:last'));
    });
}

function create_user_items(appendTo, users) {
    users = get_parsed_str(users);
    $.each(users, function(idx, user) {
        var html = get_user_item(user);
        $(appendTo).append(html);
    });
}

function get_item_warning(f_count=0, t_count=0) {
    if (f_count > t_count) {
        return `<span class="bg-warning">この投稿内容は誤っている可能性があります</span><br>`;
    }
    return '';
}

function get_created_at(created_at='') {
    return `<span class="created-at">${created_at}</span>`;
}

function get_delete_btn(is_delete=true) {
    if (is_delete) {
        return `<a class="btn btn-sm btn-outline-dark delete-confirm-button" role="button">削除</a>`;
    }
    return '';
}

function get_post_item(post, is_link=false) {
    if (is_empty(post)) {
        return '';
    }
    post = get_parsed_str(post);
    var html = `<div class="post-item-col"><div class="c-black item-object`;
    if (is_link) {
        html += ` item-link get-reply-link`;
    }
    html += `">`;

    if (post.agree_count < post.disagree_count) {
        html += `<div class="disagree-item post-item">`;
    } else {
        html += `<div class="agree-item post-item">`;
    }

    html += get_item_warning(post.false_count, post.true_count);
    html += get_post_header(post);
    html += get_post_content(post);
    html += get_item_footer(post);
    html += `</div></div></div>`;

    return html;
}

function get_post_header(post) {
    var html = `<div class="post-item-header item-header">`;
    html += get_item_user_area(post.username, post.user_img);
    html += get_item_room_area(post.room_id, post.room_title);
    html += '<div class="margin-left">';
    html += get_created_at(post.created_at);
    html += get_item_detail_link(`/post/${post.obj_id}/`);
    html += get_item_copy_link(`/post/${post.obj_id}/`);
    html += get_delete_btn(post.can_user_delete);
    html += `</div></div>`;
    return html;
}

function get_post_content(post) {
    var html = `<div class="post-content">
            <span class="post-title">${escapeHTML(post.title)}</span><br>
            <span class="post-text">${adapt_linebreaks(escapeHTML(post.text))}</span><br>
            <span class="post-source">${get_item_source(post.source)}</span>
        </div>
        <div class="file-content text-center">
        <div class="luminous-group">`;
    $.each(post.img_paths, function(idx, path) {
        if (!is_empty(path)) {
            html += `<a href="${path}" class="luminous-list-${post.obj_id} luminous-link">
                <img src="${path}" alt="" class="post-img corner-circle"></a>`;
        }
    });
    html += '</div>';
    if (is_empty(post.img_paths) & !is_empty(post.video_path)) {
        html += `<video controls src="${post.video_path}" class="post-video"></video>`;
    }
    html += '</div>';
    return html;
}

//todo replyとreply2の区別をする
function get_reply_item(reply, is_link=false) {
    if (is_empty(reply)) {
        return '';
    }
    reply = get_parsed_str(reply);
    var html = `<div class="c-black item-object`;
    if (is_link) {
        html += ` item-link get-reply2-link `;
    }
    html += `">`

    if (reply.is_agree) {
        html += `<div class="agree-item reply-item">`;
    } else if (reply.is_disagree) {
        html += `<div class="disagree-item reply-item">`;
    } else if (reply.is_neutral) {
        html += `<div class="neutral-item reply-item">`;
    } else {
        html += `<div class="empty-reply reply-item">`;
    }

    html += get_item_warning(reply.false_count, reply.true_count);
    html += get_reply_header(reply);
    html += get_reply_content(reply);
    html += get_item_footer(reply);

    html += `</div></div>`;
    return html;
}

function get_reply_header(reply) {
    var html = `<div class="reply-item-header item-header">`;
    if (reply.is_agree) {
        html += get_traffic_img(trafficGreenImg);
    } else if (reply.is_disagree) {
        html += get_traffic_img(trafficRedImg);
    } else if (reply.is_neutral) {
        html += get_traffic_img(trafficYellowImg);
    }
    if (reply.type) {
        html += `<span>#${escapeHTML(reply.type)}</span>`
    }
    html += `</div><div class="reply-item-header item-header">`;
    html += get_item_user_area(reply.username, reply.user_img);
    html += '<div class="margin-left">';
    html += get_item_detail_link(`/reply/${reply.obj_id}/`);
    html += get_item_copy_link(`/reply/${reply.obj_id}/`);
    html += get_created_at(reply.created_at);
    html += get_delete_btn(reply.can_user_delete);
    html += `</div></div>`;
    return html;
}

function get_reply_content(reply) {
    var html = `<div class="reply-content">
        <span class="reply-text">${adapt_linebreaks(escapeHTML(reply.text))}</span><br>
        <span class="reply-source">${get_item_source(reply.source)}</span>
        </div>
        <div class="file-content text-center">
        <div class="luminous-group">`;
    if (!is_empty(reply.img_path)) {
        html += `<a href="${reply.img_path}" class="luminous-list-${reply.obj_id} luminous-link">
            <img src="${reply.img_path}" alt="" class="reply-img corner-circle"></a>`;
    }
    html += '</div></div>';
    return html;
}

function get_item_footer(data) {
    var html = `<div class="footer-button item-footer" data-id="${data.obj_id}" data-type="${data.obj_type}" data-room-id="${data.room_id}">`;
    if (data.agree_state) {
        html += `<button type="button" class="agree-button btn-sm btn btn-success">賛成</button>`;
    } else {
        html += `<button type="button" class="agree-button btn-sm btn btn-outline-success">賛成</button>`;
    }
    html += `<span class="agree-count">${data.agree_count}</span>`;
    
    if (data.agree_state == false) {
        html += `<button type="button" class="disagree-button btn-sm btn btn-danger">反対</button>`;
    } else {
        html += `<button type="button" class="disagree-button btn-sm btn btn-outline-danger">反対</button>`;
    }
    html += `<span class="disagree-count">${data.disagree_count}</span>`;
    
    html += `<a class="favorite-button">`;
    if (!data.favorite_state) {
        html += `<img src="${whiteStarImg}" alt="" class="favorite-img">`;
    } else {
        html += `<img src="${yellowStarImg}" alt="" class="favorite-img">`
    }
    html += `</a><span class="favorite-count">${data.favorite_count}</span>`;

    if (data.demagogy_state) {
        html += `<button type="button" class="demagogy-button btn-sm btn btn-dark">真</button>`;
    } else {
        html += `<button type="button" class="demagogy-button btn-sm btn btn-outline-dark">真</button>`;
    }   
    html += `<span class="true-count">${data.true_count}</span>`;

    if (data.demagogy_state == false) {
        html += `<button type="button" class="disdemagogy-button btn-sm btn btn-dark">偽</button>`;
    } else {
        html += `<button type="button" class="disdemagogy-button btn-sm btn btn-outline-dark">偽</button>`;
    }   
    html += `<span class="false-count">${data.false_count}</span>`;
    if (!is_empty(data.reply_count)) {
        html += `<a href="#" role="button" class="show-modal-reply-button btn btn-sm btn-secondary">返信</a>
        <span class="reply-count">${data.reply_count}</span>`;
    }
    html += `</div>`;

    return html;
}

function get_user_item(user) {
    if (is_empty(user)) {
        return '';
    }
    user = get_parsed_str(user);
    var html = `<div class="user-item-col"><div class="item-object c-white"><div class="border user-item">`;
    html += get_user_header(user);
    html += get_user_content(user);
    html += get_user_footer(user);
    html += '</div></div></div>';

    return html;
}

function get_user_header(user) {
    return `<div class="user-item-header item-header">
    <div class="margin-left">
    ${get_item_copy_link(`/user/${user.username}/`)}
    ${get_created_at(user.created_at)}</div></div>`;
}

function get_user_content(user){
	var html = '<div class="user-item-content"><div class="user-item-img user-img-area">';
	if (!is_empty(user.img)) {
		html += `<img src="${user.img}" alt="" class="user-img">`;
	} else {
		html += `<img src="${humanImg}" alt="" class="user-img">`;
    }
	html += `</div><div class="username"><div class="headline">ユーザー名</div>${escapeHTML(user.username)}</div>
	<div class="user-profession"><div class="headline">職業</div>${escapeHTML(user.profession)}</div>
	<div class="user-description"><div class="headline">詳細</div>${adapt_linebreaks(escapeHTML(user.description))}</div></div>`;

	return html;
}

function get_user_footer(user) {
    var html = `<div class="footer-button item-footer" data-username="${user.username}">`;
    if (user.is_block) {
        html += `<button type="button" class="block-button btn btn-secondary">ブロック解除</button>`;
    } else {
        if (user.is_follow) {
            html += `<button type="button" class="follow-button btn btn-secondary">フォロー解除</button>`;
        } else {
            html += `<button type="button" class="follow-button btn btn-outline-secondary">フォロー</button>`;
        }
        html += `<span class="followed-count">${user.followed_count}</span>
        <button type="button" class="block-button btn btn-outline-secondary">ブロック</button>`;
    }

    html += `<span class="blocked-count">${user.blocked_count}</span></div>`;

    return html;
}

function get_room_item(room) {
    if (is_empty(room)) {
        return '';
    }
    room = get_parsed_str(room);
    var html = `<div class="room-item-col"><div class="item-object c-white">
    <div class="border room-item">`;
    html += get_room_header(room);
    html += get_room_content(room);
    html += get_room_footer(room);
    html += `</div></div></div>`;

    return html;
}

function get_room_header(room) {
    return `<div class="room-item-header item-header">
    ${get_item_user_area(room.admin, room.admin_img, 'white')}
    <div class="margin-left">
    ${get_item_copy_link(`/room/${room.id}/`)}
    ${get_created_at(room.created_at)}</div></div>`;
}

function get_room_content(room) {
    var html = `<div class="room-item-content">
        <div class="room-item-title">
            <span>${escapeHTML(room.title)}</span>
        </div>
        <div class="room-item-subtitle">
            <span>${adapt_linebreaks(escapeHTML(room.subtitle))}</span>
        </div>`;
    if (!is_empty(room.video_path)) {
        html += `<div class="video-area px-1">
        <video controls src="${room.video_path}" class="w-100"></video>
        </div>`;
    } else if (!is_empty(room.img_paths)) {
        html += `<div class="room-item-img">${get_slider_imgs_html('search-room-slider', room.img_paths)}</div>`;
    }
    html += `</div>
    <div class="thinking">
        参加人数：<span>${room.user_count}</span>
    </div>`

    return html;
}

function get_room_footer(room) {
    var html = `<div class="footer-button item-footer" data-id="${room.id}" data-type="room">
    <button data-href="/room/${room.id}/" class="new-window-open btn btn-secondary" type="button">移動</button>`;
    if (room.good_state) {
        html += `<button type="button" class="good-button btn btn-success">Good</button>`;
    } else {
        html += `<button type="button" class="good-button btn btn-outline-success">Good</button>`;
    }
    html += `<span class="good-count">${room.good_count}</span>`;
    if (room.good_state == false) {
        html += `<button type="button" class="bad-button btn btn-danger">Bad</button>`;
    } else {
        html += `<button type="button" class="bad-button btn btn-outline-danger">Bad</button>`;
    }
    html += `<span class="bad-count">${room.bad_count}</span>
    </div>`;

    return html;
}

function get_slider_imgs_html(cls, img_paths) {
    if (is_empty(img_paths)) {
        return '';
    }

    if (img_paths.length == 1) {
        return `<img src="${img_paths[0]}" class="corner-circle">`;
    }

    var html = `<ul class="slider ${cls}">`;
    $.each(img_paths, function(idx, img_path) {
        html += `<li><img src="${img_path}" class="corner-circle"></li>`;
    });
    html += `</ul>`
    
    return html;
}

function get_item_user_area(name, img=null, color='black') {
    var html = `<div class="item-header-user-img user-img-area">`;
    if (is_empty(img)) {
        html += `<img src="${humanImg}" alt="" class="user-img">`;
    } else {
        html += `<img src="${img}" alt="" class="user-img">`;
    }
    html += `</div><a class="c-${color} show-modal-user-button" href="#" data-username="${name}">${name}</a>`;
    return html;
}

function get_item_room_area(room_id, title, color='black') {
    if (!is_empty(room_id)) {
        return `<img src="${houseImg}" class="house-img"><a class="c-${color} show-modal-room-button" href="#" data-roomid="${room_id}">${title}</a>`;
    }
    return '';
}

function get_item_source(source, color='blue') {
    if (!is_empty(source)) {
        return `【ソース】<a class="c-${color}" href="${escapeHTML(source)}">${escapeHTML(source)}</a>`; 
    }
    return '';
}

function create_search_room_result(room) {
    room = get_parsed_str(room);
    return `<div class="search-result">
    ${get_item_user_area(room.admin, room.user_img, 'white')}
    ${get_item_room_area(room.id, room.title, 'white')}
    <a href="/room/${room.id}/" class="btn btn-secondary btn-sm" role="button">移動</a></div>`;
}

function create_search_user_result(user) {
    user = get_parsed_str(user);
    return `<div class="search-result">
    ${get_item_user_area(user.username, user.user_img, 'white')}
    <button type="button" data-username="${user.username}" class="invite-user btn btn-secondary btn-sm">招待</button></div>`;
}

function create_myroom_dropdown(id, title) {
    $('.myroom-list').prepend(`<a class="dropdown-item" href="/room/${id}/">${escapeHTML(title)}</a>`);
}

function get_item_detail_link(path) {
    return `<a href="${path}"><img src="${goDetailImg}" alt="" class="go-detail-img"></a>`;
}

function get_item_copy_link(path) {
    return `<img src="${copyLinkImg}" alt="" data-link="${BASE_URL}${path}" class="copy-link-img copy-link">`;
}

function get_traffic_img(src) {
    return `<img src="${src}" class="traffic-light">`;
}

function get_question_img() {
    return `<img src="${questionImg}" class="question-img">`;
}

function get_human_img() {
    return `<img src="${humanImg}" class="user-img">`;
}

function get_trash_img() {
    return `<img src="${trashImg}" class="trash-img">`;
}

function get_add_img() {
    return `<img src="${addImg}" class="img-add-button">`;
}

function get_lock_img() {
    return `<img src="${lockImg}" class="lock-room">`;
}

function get_post_img() {
    return `<img src="${postImg}">`;
}

function get_phone_img() {
    return `<img src="${phoneImg}">`;
}

function get_web_img() {
    return `<img src="${webImg}">`;
}

function get_map_img() {
    return `<img src="${mapImg}">`;
}

function get_calender_img() {
    return `<img src="${calenderImg}">`;
}