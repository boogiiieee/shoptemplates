jQuery.fn.titleform = function(fields){
	return this.each(function() {
		for (var key in fields) {
			jQuery(this).find(key).each(function(){
				var field = jQuery(this);
				var name = fields[key];
				
				if (field.val() == ''){ field.val(name); }
				field.focusin(function(){
					if ($(this).val() == name){ $(this).val(''); } 
				});
				field.focusout(function(){
					if ($(this).val() == ''){ $(this).val(name); }
				});
			});
		}
		
		jQuery(this).submit(function(){
			for (var key in fields) {
				jQuery(this).find(key).each(function(){
					var field = jQuery(this);
					var name = fields[key];
					if (field.val() == name){ field.val(''); }
				});
			}
		});
	});
};

$(document).ready(function(){
	$('.zakaz form').titleform({
		'#id_name':'Имя и фамилия *',
		'#id_email':'E-mail *',
		'#id_phone':'Мобильный телефон *',
		'#id_text':'Комментарий'
	});
});
