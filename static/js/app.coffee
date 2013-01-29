$('.enroll').click ()->
	pathname = window.location.pathname
	data = {placeholder:'hello'}
	$.post(pathname,data,(d,st,xr)->
		$('.enroll').remove()
		)

$('.startClass').click ()->
	pathname = window.location.pathname
	$.get(pathname+'match',(d,st,xr)->
		$.noop()
		)

$('.finishbtn').click ()->
	coursename = $(this).attr('coursename')
	nid = $(this).attr('noteid')
	herp = $(this)
	$.post('/'+coursename+'/'+nid+'/done',(d,st,xr)->
		herp.parent().remove()
		)

window.inplace = (content)->
    path = window.location.pathname
    $.post(path+'/new',{newval:content},(d,st,xr)->
        $.noop()
        )

if window.location.pathname=="/"
	$('footer').css('border','none')