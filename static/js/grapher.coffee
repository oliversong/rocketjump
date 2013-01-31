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
	        $('.duderow1 > div:first').remove();
	        $('.duderow2 > div:first').remove();
	        $('.duderow3 > div:first').remove();

	        #update values
	        $('.numConnect').text(x[2])
	        $('.numQueued').text(x[0])
	        $('.numEnrolled').text(x[1])

	        # Get the current max value

	        # Add in new value and scale heights
	        $('.duderow1').append('<div class="span1 datapoint" style="height:'+x[1]*0.01*300+'px"><span class="intext">'+x[1]+'</span></div>')
	        $('.duderow2').append('<div class="span1 datapoint" style="height:'+x[2]*0.01*300+'px"><span class="intext">'+x[2]+'</span></div>')
	        $('.duderow3').append('<div class="span1 datapoint" style="height:'+x[0]*0.01*300+'px"><span class="intext">'+x[0]+'</span></div>')
	        
	        #Setup the next poll recursively
	        poll()
	    )
    ), 2000
)()