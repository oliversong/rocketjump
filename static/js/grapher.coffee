parse = (str, separator) ->
  parsed = {}
  pairs = str.split(separator)
  i = 0
  len = pairs.length
  keyVal = undefined

  while i < len
    keyVal = pairs[i].split("=")
    parsed[keyVal[0]] = keyVal[1]  if keyVal[0]
    ++i
  parsed

(poll = ->
	pathname = window.location.pathname
	console.log(pathname)
	setTimeout (->
	    $.post(pathname+'/polll',(d,st,xr)->
	        console.log(d)
	        d = d.replace(/\'/g, '');
	        shit = $.parseJSON(d)
	        console.log shit

	        # take off the first div
	        #$('.dudegraph div').remove()
	        $('.duderow > div:first').remove();

	        # Get the current max value

	        # Add in new value and scale heights
	        f = shit['taking']+shit['queuelength']
	        console.log(f)
	        $('.duderow').append('<div class="span1 datapoint" style="height:'+f*0.05*300+'px></div>')
	        
	        #Setup the next poll recursively
	        poll()
	    )
    ), 2000
)()