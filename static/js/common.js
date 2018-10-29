function timeConverter(UNIX_timestamp){
      var a = new Date(UNIX_timestamp * 1000);
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var year = a.getFullYear();
      var month = months[a.getMonth()];
      var date = a.getDate();
      var hour = a.getHours();
      var min = a.getMinutes();
      var sec = a.getSeconds();
      var time = date + '/' + month + '/' + year + ' ' + hour + ':' + min + ':' + sec ;
      return time;
}

var didScroll;
var lastScrollTop = 0;
var delta = 5;
var navbarHeight = 50;

$(window).scroll(function(event) {
  didScroll = true;
});

setInterval(function() {
  if (didScroll) {
    hasScrolled();
    didScroll = false;
  }
}, 250);

function hasScrolled() {
  var st = $(this).scrollTop();

  // Make sure they scroll more than delta
  if (Math.abs(lastScrollTop - st) <= delta)
    return;

  // If they scrolled down and are past the navbar, add class .nav-up.
  // This is necessary so you never see what is "behind" the navbar.
  if (st > lastScrollTop && st > navbarHeight) {
    // Scroll Down
    $('header').removeClass('header-down').addClass('header-up');
    // $('.logo-img').empty()
    // $('.logo-img').append('<img src="/static/img/logo_blanco.png">')
  } else {
    // Scroll Up
    console.log(st, $(window).height(), $(document).height(), st <= 10)
    if (st <= 50) {
      $('header').removeClass('header-up').addClass('header-down');
      // $('.logo-img').empty()
    }
  }

  lastScrollTop = st;
}

function showStickySuccessToast() {        
      $().toastmessage('showToast', 
        { text     : 'Success Dialog which is sticky',            
        sticky   : true,            
        position : 'top-right',            
        type     : 'success',            
        closeText: '',            
        close    : function () {                
        console.log("toast is closed ...");            
        }        
     });    
} 