// Generated by CoffeeScript 1.4.0
(function() {

  $('#helloThere').modal({
    'keyboard': false
  });

  $('.meetNewPeople').click(function() {
    var data;
    data = {
      intent: 'meetnew'
    };
    return $.post('/intent', data, function(d, st, xr) {
      return $('#myModal').modal('hide');
    });
  });

  $('.meetSpecial').click(function() {
    var data;
    data = {
      intent: 'special'
    };
    return $.post('/intent', data, function(d, st, xr) {
      return $('#myModal').modal('hide');
    });
  });

}).call(this);
