$('.enroll').click ()->
	pathname = window.location.pathname
	data = {placeholder:'hello'}
	$.post(pathname,data,(d,st,xr)->
		console.log("Successfully enrolled")
		$('.enroll').remove()
		)

$('.startClass').click ()->
	pathname = window.location.pathname
	$.get(pathname+'match',(d,st,xr)->
		console.log("Boom")
		)

$('.finishbtn').click ()->
	id = $(this).attr('noteid')
	course = $(this).attr('coursename')
	$.post('/'+course+'/'+id+'/done',(d,st,xr)->
		console.log('Class dismissed')
		)