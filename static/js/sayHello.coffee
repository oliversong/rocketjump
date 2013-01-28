$('#helloThere').modal({'keyboard':false})

$('.meetNewPeople').click ()->
	data = {intent:'meetnew'}
	$.post('/intent',data, (d,st,xr)->
		$('#helloThere').modal('hide')
		)

$('.meetSpecial').click ()->
	data = {intent:'special'}
	$.post('/intent',data, (d,st,xr)->
		$('#helloThere').modal('hide')
		)