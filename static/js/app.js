// Generated by CoffeeScript 1.4.0
(function() {

  $('.enroll').click(function() {
    var data, pathname;
    pathname = window.location.pathname;
    data = {
      placeholder: 'hello'
    };
    return $.post(pathname, data, function(d, st, xr) {
      console.log("Successfully enrolled");
      return $('.enroll').remove();
    });
  });

  $('.startClass').click(function() {
    var pathname;
    pathname = window.location.pathname;
    return $.get(pathname + 'match', function(d, st, xr) {
      return console.log("Boom");
    });
  });

}).call(this);
