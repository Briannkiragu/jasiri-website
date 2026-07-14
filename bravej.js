const bar = document.getElementById('bar');
const nav = document.getElementById('navbar');
const close = document.getElementById('close');

if(bar){
bar.addEventListener('click', () =>{
    nav.classList.add('active')
})
}

if(close){
close.addEventListener('click', () =>{
    nav.classList.remove('active')
})
}



/*about zoomblur*/
$(function(){
    zoom = $('.feature').css('background-size')
    zoom = parseFloat(zoom)/100
    size = zoom * $('.feature').width();
    $(window).on('scroll', function(){
      fromTop = $(window).scrollTop();
      newSize = size - (fromTop/3);
      if (newSize > $('.feature').width()) {
          $('.feature').css({
              '-webkit-background-size': newSize,
              '-moz-background-size': newSize,
              '-o-background-size': newSize,
              'background-size': newSize,
              '-webkit-filter':'blur('+ 0 + (fromTop/100) + 'px)',
              'opacity': 1 - ((fromTop / $('html').height()) * 1.3)
          });
      }
    });
});

$(function (){
    var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);

    if (isChrome || isSafari) {
    } else {
        $('.feature').append('<div class="opaque"></div>');
        $(window).on('scroll', function(){
            var opacity = 0 + ($(window).scrollTop()/5000);
            $('.opaque').css('opacity', opacity);
        });
    }
});

/*blog credits fx*/
lasScrTop = 0;
opa = 1;
sca = 5;
$(window).scroll(function () {
  winTop = $(this).scrollTop();
  winMid = $(window).height() / 2 + winTop;
  winBot = $(window).height() + winTop;
  // scroll到li,執行動態
  $(".scroll-wrap li").each(function () {
    liHei = $(this).height();
    liOff = $(this).offset();
    liTop = liOff.top;
    liBot = liTop + liHei;
    if (liBot <= winMid || liTop >= winBot) {
      // li滑出視窗時移除 inView
      $(this).removeClass("inView");
    } else if (liTop <= winMid) {
      // li滑到中間時，加入 inView
      $(this).addClass("inView");
    }
    inViewEq = $(".inView").index() + 1;
    console.log(inViewEq);
    $(".movie")
      .attr("class", "")
      .addClass("movie step-" + inViewEq);
  });
  // 判斷scroll往上滑或往下滑
  if (winTop > lasScrTop) {
    // 往下滑
  } else {
    // 往上滑
  }
  lasScrTop = winTop;
});
