$(() => $("time.timeago").timeago());

$(() => GOVUK.stickAtTopWhenScrolling.init());

$(() => GOVUK.modules.start());

$(() => $('.error-message').eq(0).parent('label').next('input').trigger('focus'));

$(() => $('.banner-dangerous').eq(0).trigger('focus'));

console.log('hey');

$(function() {
  var c = $(".fullscreen-container");
  var ch = c.innerHeight();
  var cTop = c.offset().top;
  var shim = $("<div/>");
  shim.css({
    'height': ch,
    'width': 1,
    'position': 'absolute',
    'top': cTop
  });
  c.after(shim);

  $(window).on('scroll resize', function() {
    var vp = $(window).height();
    var st = $('html, body').scrollTop();
    c.css(
      'max-height',
      Math.min(
        vp - cTop + st,
        ch
      )
    );
  });

});
