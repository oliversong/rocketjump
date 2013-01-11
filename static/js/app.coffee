$('.enroll').click ()->
	pathname = window.location.pathname
	data = {placeholder:'hello'}
	$.post(pathname,data,(d,st,xr)->
		console.log("Successfully enrolled")
		$('.enroll').remove()
		)