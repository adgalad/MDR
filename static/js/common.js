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
    if (st <= 50) {
      $('header').removeClass('header-up').addClass('header-down');
      // $('.logo-img').empty()
    }
  }

  lastScrollTop = st;
}









// TOAST **********************************//
var settings = {
    inEffect:       {opacity: 'show'},  // in effect
    inEffectDuration:600,        // in effect duration in miliseconds
    stayTime:        3000,       // time in miliseconds before the item has to disappear
    text:            '',         // content of the item. Might be a string or a jQuery object. Be aware that any jQuery object which is acting as a message will be deleted when the toast is fading away.
    sticky:          false,        // should the toast item sticky or not?
    type:            'notice',       // notice, warning, error, success
    position:        'top-right',        // top-left, top-center, top-right, middle-left, middle-center, middle-right ... Position of the toast container holding different toast. Position can be set only once at the very first call, changing the position after the first call does nothing
    closeText:       '',                 // text which will be shown as close button, set to '' when you want to introduce an image via css
    close:           null                // callback function when the toastmessage is closed
};

var methods = {
  init : function(options)
  {
    if (options) {
            $.extend( settings, options );
        }
  },

  showToast : function(options)
  {
    var localSettings = {};
        $.extend(localSettings, settings, options);

    // declare variables
        var toastWrapAll, toastItemOuter, toastItemInner, toastItemClose, toastItemImage;

    toastWrapAll  = (!$('.toast-container').length) ? $('<div></div>').addClass('toast-container').addClass('toast-position-' + localSettings.position).appendTo('body') : $('.toast-container');
    toastItemOuter  = $('<div></div>').addClass('toast-item-wrapper');
    toastItemInner  = $('<div></div>').hide().addClass('toast-item toast-type-' + localSettings.type).appendTo(toastWrapAll).html($('<p>').append (localSettings.text)).animate(localSettings.inEffect, localSettings.inEffectDuration).wrap(toastItemOuter);
    toastItemClose  = $('<div></div>').addClass('toast-item-close').prependTo(toastItemInner).html(localSettings.closeText).click(function() { toastmessage('removeToast',toastItemInner, localSettings) });
    toastItemImage  = $('<div></div>').addClass('toast-item-image').addClass('toast-item-image-' + localSettings.type).prependTo(toastItemInner);

        if(navigator.userAgent.match(/MSIE 6/i))
    {
        toastWrapAll.css({top: document.documentElement.scrollTop});
      }

    if(!localSettings.sticky)
    {
      setTimeout(function()
      {
        toastmessage('removeToast', toastItemInner, localSettings);
      },
      localSettings.stayTime);
    }
        return toastItemInner;
  },

  showNoticeToast : function (message)
  {
      var options = {text : message, type : 'notice'};
      return toastmessage('showToast', options);
  },

  showSuccessToast : function (message)
  {
      var options = {text : message, type : 'success'};
      return toastmessage('showToast', options);
  },

  showErrorToast : function (message)
  {
      var options = {text : message, type : 'error'};
      return toastmessage('showToast', options);
  },

  showWarningToast : function (message)
  {
      var options = {text : message, type : 'warning'};
      return toastmessage('showToast', options);
  },

  removeToast: function(obj, options)
  {
    obj.animate({opacity: '0'}, 600, function()
    {
      obj.parent().animate({height: '0px'}, 300, function()
      {
        obj.parent().remove();
      });
    });
        // callback
        if (options && options.close !== null)
        {
            options.close();
        }
  }
};

toastmessage = function( method ) {

    // Method calling logic
    if ( methods[method] ) {
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.toastmessage' );
    }
};

// END TOAST ************************************//


function checkNotifications(){
  const Http = new XMLHttpRequest();
  const url='/api/user/notifications';
  Http.open("GET", url);
  Http.send();
  Http.onreadystatechange=function(){
    if (Http.readyState==4 && Http.status==200){
      data = JSON.parse(Http.responseText)
      notifications = data['notifications']
      for (var i = 0; i < notifications.length; i++){
        showStickySuccessToast(notifications[i]['message'])
      }
    }
  }
}

function showStickySuccessToast(message) {
      toastmessage('showToast', {
            text     : message,
            sticky   : true,
            position : 'top-right',
            type     : 'success',
            closeText: '',
            close    : function () {
            }
        });  
} 


