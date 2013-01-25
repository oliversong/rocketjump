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
	id = $(this).attr('noteid')
	course = $(this).attr('coursename')
	$.post('/'+course+'/'+id+'/done',(d,st,xr)->
		$.noop()
		)

///$('.noteName').click ()->
	blah = $(this).text()
	id = $(this).attr('noteid')
	course = $(this).attr('coursename')
	$(this).replaceWith('''<span class="replaceme"><input type="text" class="nameReplace" name="nameReplace" placeholder="'''+blah+'''
		" />
		<button class="btn btn-warning updateName">Update</button></span>
		''')
	$('.updateName').click ()->
		newName = $('.nameReplace').val()
		$.post('/'+course+'/'+id+'/updateName',{ name:newName },(d,st,xr)->
			$('.replaceme')
			)
///
window.inplace = (content)->
	path = window.location.pathname
	$.post(path+'/new',{newval:content},(d,st,xr)->
		$.noop()
		)


if window.location.pathname=="/"
	$('footer').css('border','none')