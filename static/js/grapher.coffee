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
	        x=$.parseJSON(d)

	        # take off the first div
	        $('.duderow > div:first').remove();

	        #update values
	        $('.numConnect').text(x[2])
	        $('.numQueued').text(x[0])
	        $('.numEnrolled').text(x[1])

	        # Get the current max value

	        # Add in new value and scale heights
	        $('.duderow').append('<div class="span1 datapoint" style="height:'+x[2]*0.05*300+'px"><span class="intext">'+x[2]+'</span></div>')
	        
	        #Setup the next poll recursively
	        poll()
	    )
    ), 2000
)()