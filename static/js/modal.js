$.validator.addMethod("dateFormat",
	function (value, element) {
		if (value.trim() == '') {
			return true;
		}
		return value.match(/^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$/);
	},"yyyy-mm-ddの形式で入力してください");

$(document).ready(function() {
	$("form[id='signup-form']").validate({
		rules:{
			email:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				email:true,
				maxlength:EMAIL_MAX_LENGTH,
			},
			username:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:USERNAME_MAX_LENGTH,
			},
			password:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
			},
			password_confirm:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
				equalTo: "#password",
			}
		},

		messages:{
			email:{
				required:get_required_message(),
				email:get_email_message(),
				maxlength:get_lte_message(EMAIL_MAX_LENGTH),
			},
			username:{
				required:get_required_message(),
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			password:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
			},
			password_confirm:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
				equalTo:get_equal_message("パスワード"),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='signup-send-mail-form']").validate({
		rules:{
			email:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					},
				},
				email:true,
				maxlength:EMAIL_MAX_LENGTH,
			},
		},

		messages:{
			email:{
				required:get_required_message(),
				email:get_email_message(),
				maxlength:get_lte_message(EMAIL_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	})

	$("form[id='reset-password-form']").validate({
		rules:{
			password:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					},
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
			},
			password_confirm:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
				equalTo: "#password",
			}
		},

		messages:{
			password:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
			},
			password_confirm:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
				equalTo:get_equal_message("パスワード"),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='reset-password-send-mail-form']").validate({
		rules:{
			username:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:USERNAME_MAX_LENGTH,
			},
			email:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				email:true,
				maxlength:EMAIL_MAX_LENGTH,
			},
		},

		messages:{
			username:{
				required:get_required_message(),
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			email:{
				required:get_required_message(),
				email:get_email_message(),
				maxlength:get_lte_message(EMAIL_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='change-password-form']").validate({
		rules:{
			password:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
			},
			password_confirm:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				minlength:PASSWORD_MIN_LENGTH,
				maxlength:PASSWORD_MAX_LENGTH,
				equalTo: "#password",
			}
		},

		messages:{
			password:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
			},
			password_confirm:{
				required:get_required_message(),
				minlength:get_gte_message(PASSWORD_MIN_LENGTH),
				maxlength:get_lte_message(PASSWORD_MAX_LENGTH),
				equalTo:get_equal_message("パスワード"),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='reply-form']").validate({
		rules:{
			text:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},				
				maxlength:REPLY_TEXT_MAX_LENGTH,
			},
			url:{
				maxlength:REPLY_URL_MAX_LENGTH,
			},
			img:{
				extension: IMAGE_EXTENSION,
			}
		},

		messages:{
			text:{
				required:get_required_message(),
				maxlength:get_lte_message(REPLY_TEXT_MAX_LENGTH),
			},
			url:{
				maxlength:get_lte_message(REPLY_URL_MAX_LENGTH),
			},
			img:{
				extension:get_extension_message(IMAGE_EXTENSION),
			}
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='post-form']").validate({
		rules:{
			title:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:POST_TITLE_MAX_LENGTH,
			},
			text:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:POST_TEXT_MAX_LENGTH,
			},
			img:{
				extension: IMAGE_EXTENSION,
			},
			video:{
				extension: VIDEO_EXTENSION,
			},
		},

		messages:{
			title:{
				required:get_required_message(),
				maxlength:get_lte_message(POST_TITLE_MAX_LENGTH),
			},
			text:{
				required:get_required_message(),
				maxlength:get_lte_message(POST_TEXT_MAX_LENGTH),
			},
			img:{
				extension:get_extension_message(IMAGE_EXTENSION),
			},
			video:{
				extension:get_extension_message(VIDEO_EXTENSION),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='create-room-form']").validate({
		rules:{
			title:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:ROOM_TITLE_MAX_LENGTH,
			},
			subtitle:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:ROOM_SUBTITLE_MAX_LENGTH,
			},
			img:{
				extension: IMAGE_EXTENSION
			}
		},

		messages:{
			title:{
				required:get_required_message(),
				maxlength:get_lte_message(ROOM_TITLE_MAX_LENGTH),
			},
			subtitle:{
				required:get_required_message(),
				maxlength:get_lte_message(ROOM_SUBTITLE_MAX_LENGTH),
			},
			img:{
				extension:get_extension_message(IMAGE_EXTENSION),
			}
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='search-post-form']").validate({
		rules:{
			username:{
				maxlength:USERNAME_MAX_LENGTH,
			},
			title:{
				maxlength:POST_TITLE_MAX_LENGTH,
			},
			date_from:{
				dateFormat:true,
			},
			date_to:{
				dateFormat:true,
			},
		},

		messages:{
			username:{
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			title:{
				maxlength:get_lte_message(POST_TITLE_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='search-pir-form']").validate({
		rules:{
			username:{
				maxlength:USERNAME_MAX_LENGTH,
			},
			title:{
				maxlength:POST_TITLE_MAX_LENGTH,
			},
			date_from:{
				dateFormat:true,
			},
			date_to:{
				dateFormat:true,
			},
		},

		messages:{
			username:{
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			title:{
				maxlength:get_lte_message(POST_TITLE_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='search-reply-form']").validate({
		rules:{
			username:{
				maxlength:USERNAME_MAX_LENGTH,
			},
			test:{
				maxlength:REPLY_TEXT_MAX_LENGTH,
			},
			date_from:{
				dateFormat:true,
			},
			date_to:{
				dateFormat:true,
			},
		},

		messages:{
			username:{
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			test:{
				maxlength:get_lte_message(REPLY_TEXT_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='search-room-form']").validate({
		rules:{
			username:{
				maxlength:USERNAME_MAX_LENGTH,
			},
			title:{
				maxlength:ROOM_TITLE_MAX_LENGTH,
			},
			date_from:{
				dateFormat:true,
			},
			date_to:{
				dateFormat:true,
			},
		},

		messages:{
			username:{
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			title:{
				maxlength:get_lte_message(ROOM_TITLE_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='search-user-form']").validate({
		rules:{
			username:{
				maxlength:USERNAME_MAX_LENGTH,
			},
			profession:{
				maxlength:PROFESSION_MAX_LENGTH,
			},
			description:{
				maxlength:DESCRIPTION_MAX_LENGTH,
			},
			date_from:{
				dateFormat:true,
			},
			date_to:{
				dateFormat:true,
			},
		},

		messages:{
			username:{
				maxlength:get_lte_message(USERNAME_MAX_LENGTH),
			},
			profession:{
				maxlength:get_lte_message(PROFESSION_MAX_LENGTH),
			},
			description:{
				maxlength:get_lte_message(DESCRIPTION_MAX_LENGTH),
			},
		},

		submitHandler: function(form) {
			form.submit();
		},
	});

	$("form[id='manage-room-display-form']").validate({
		rules:{
			title:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:ROOM_TITLE_MAX_LENGTH,
			},
			subtitle:{
				required:{
					depends:function(){
						$(this).val($(this).val().trimStart());
						return true;
					}
				},
				maxlength:ROOM_SUBTITLE_MAX_LENGTH,
			},
			img:{
				extension: IMAGE_EXTENSION,
			},
			video:{
				extension: VIDEO_EXTENSION,
			},
		},

		messages:{
			title:{
				required:get_required_message(),
				maxlength:get_lte_message(ROOM_TITLE_MAX_LENGTH),
			},
			subtitle:{
				required:get_required_message(),
				maxlength:get_lte_message(ROOM_SUBTITLE_MAX_LENGTH),
			},
			img:{
				extension:get_extension_message(IMAGE_EXTENSION),
			},
            video:{
				extension:get_extension_message(VIDEO_EXTENSION),
			}
		},
	});

	// $("tr[class='manage-information-form']").validate({
	// 	rules:{
	// 		title:{
	// 			required:{
	// 				depends:function(){
	// 					$(this).val($(this).val().trimStart());
	// 					return true;
	// 				},
	// 			},
	// 			maxlength:EMAIL_MAX_LENGTH,
	// 		},
	// 	},

	// 	messages:{
	// 		title:{
	// 			required:get_required_message(),
	// 			maxlength:get_lte_message(EMAIL_MAX_LENGTH),
	// 		},
	// 	},

	// 	submitHandler: function(form) {
	// 		form.submit();
	// 	},
	// });

	$("form[id='manage-user-form']").validate({
		submitHandler: function(form) {
			form.submit();
		},
	});
});

function get_required_message() {
	return '入力必須';
}
function get_equal_message(name) {
	return `同じ${name}を入力してください`;
}
function get_email_message() {
	return '正しいメールアドレスを入力してください';
}
function get_gte_message(len) {
	return `${len}文字以上を入力してください`;
}
function get_lte_message(len) {
	return `${len}文字以内で入力してください`;
}
function get_only_integer() {
	return '数値のみで入力してください';
}
function get_between_length_message(min_length, max_length) {
	if (!is_int(min_length)) {
		return get_lte_message(max_length);
	} else if (!is_int(max_length)) {
		return get_gte_message(min_length);
	}
	return `${min_length}~${max_length}文字の範囲で入力してください`;
}
function get_extension_message(extension) {
	var message = '';
	$.each(extension.split('|'), function(idx, value) {
		message += `${value}, `;
	});

	return message + 'の拡張子のファイルのみをアップロードできます';
}

$(document).on('click', '.show-modal-user-button', function() {
    $.ajax({
        url:`/get/user/${$(this).data('username')}/`,
        type:'POST',
    }).done(function (data) {
		if (is_error(data)) {
            return false;
        }
		$('#modal-user').find('.modal-title').html('ユーザー詳細');
		$('#modal-user').find('.modal-body').html(get_user_header(data) + get_user_content(data));
		$('#modal-user').find('.modal-footer').html(get_user_footer(data));
		show_modal('modal-user');
    });
});

$(document).on('click', '.show-modal-room-button', function() {
    $.ajax({
        url:`/get/room/${$(this).data('roomid')}/`,
        type:'POST',
    }).done(function (data) {
		if (is_error(data)) {
            return false;
        }
		$('#modal-room').find('.modal-title').html('Room詳細');
		$('#modal-room').find('.modal-body').html(get_room_header(data) + get_room_content(data));
		$('#modal-room').find('.modal-footer').html(get_room_footer(data));
		show_modal('modal-room');
		active_slick_room_item();
    });
});

var room_reply_types = {'room':[], 'reply_types':[]};
$(document).on('click', '.show-modal-reply-button', function() {
	var obj = get_item_data($(this));
	if (room_reply_types.room.includes(obj.roomId)) {
		show_reply_types(obj, room_reply_types.reply_types[room_reply_types.room.indexOf(obj.roomId)]);
		return false;
	}

	$.ajax({
        url: `/get/reply-types/${obj.type}/${obj.id}/`,
        type:'GET',
        dataType:'json'  
    }).done(function (data) {
		if (is_error(data)) {
            return false;
        }
		room_reply_types.room.push(obj.roomId);
		room_reply_types.reply_types.push(data.reply_types);
		show_reply_types(obj, data.reply_types);
	});
});

function show_reply_types(obj, reply_types) {
	var reply_type_html = '';
	for (var i=0; i < reply_types.length; i++) {
		if (is_empty(reply_types[i])) {
			continue;
		}
		reply_type_html += `<option value="${reply_types[i]}">${reply_types[i]}</option>`;
	}

	$('#reply-form').find('.select-reply-type').html(reply_type_html);
	$('#reply-form').find('#submit-reply-button').data('href', `/${obj.type}/${obj.id}/reply/`);

	show_modal('modal-reply');
}

$('.modal').on('shown.bs.modal', function() {
	$(this).find('input.form-control').first().trigger('focus');
});