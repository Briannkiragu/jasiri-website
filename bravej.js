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
if (window.jQuery) {
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
} else {
  console.warn('jQuery not found: skipping legacy scroll effects in bravej.js');
}

/* Cart module: simple localStorage cart, add-from-products, render on Cart.html */
(function(){
  const STORAGE_KEY = 'jasiri_cart_v1';

  function getCart(){
    const storedCart = localStorage.getItem(STORAGE_KEY);
    if (storedCart === null) return [];

    const cart = JSON.parse(storedCart);
    if (!Array.isArray(cart)) {
      throw new TypeError('Stored cart data must be an array.');
    }
    return cart;
  }
  function saveCart(cart){ localStorage.setItem(STORAGE_KEY, JSON.stringify(cart)); }

  function findPriceFromPro(pro){
    const priceEl = pro.querySelector('.price') || pro.querySelector('.description h4') || pro.querySelector('.description h5');
    if(!priceEl) return 0;
    const txt = priceEl.textContent || '';
    const nums = txt.replace(/,/g,'').match(/\d+/g);
    return nums ? parseInt(nums.join('')) : 0;
  }

  function findTitleFromPro(pro){
    const title = pro.querySelector('.description h5') || pro.querySelector('.description span');
    return title?.textContent.trim() || pro.querySelector('img')?.alt?.trim() || 'Product';
  }

  function addToCart(item){
    const cart = getCart();
    // try merge by id (if provided)
    if(item.id){
      const idx = cart.findIndex(i=>i.id===item.id);
      if(idx > -1){ cart[idx].qty += item.qty; saveCart(cart); return; }
    }
    cart.push(item);
    saveCart(cart);
  }

  function getDetailPrice(context){
    const priceEl = context?.querySelector('h2') || context?.querySelector('h4.price') || context?.querySelector('h4');
    if(!priceEl) return 0;
    const txt = priceEl.textContent || '';
    const nums = txt.replace(/,/g,'').match(/\d+/g);
    return nums ? parseInt(nums.join('')) : 0;
  }

  function getDetailTitle(context){
    const titleEl = context?.querySelector('h4') || context?.querySelector('h6') || context?.querySelector('span');
    if(titleEl && titleEl.textContent.trim().length) return titleEl.textContent.trim();
    return context?.querySelector('img')?.alt?.trim() || 'Product';
  }

  function getDetailQty(context){
    const qtyInput = context?.querySelector('input[type=number]');
    if(!qtyInput) return 1;
    const qty = parseInt(qtyInput.value, 10);
    return isNaN(qty) || qty < 1 ? 1 : qty;
  }

  // enhance product cards: inject Add to Cart button if none
  function enhanceProducts(){
    document.querySelectorAll('.pro').forEach(pro=>{
      if(pro.querySelector('.add-to-cart')) return;
      const btn = document.createElement('button');
      btn.className = 'add-to-cart';
      btn.textContent = 'Add to cart';
      const desc = pro.querySelector('.description');
      if(desc) desc.appendChild(btn);
      btn.addEventListener('click', (e)=>{
        e.preventDefault();
        e.stopPropagation();
        const price = findPriceFromPro(pro) || 0;
        const title = findTitleFromPro(pro);
        const img = pro.querySelector('img')?.getAttribute('src') || '';
        const id = (title + '_' + img).replace(/\s+/g,'_').slice(0,120);
        addToCart({ id, title, price, qty:1, img });
        btn.textContent = 'Added to cart';
        btn.classList.add('added');
        setTimeout(() => {
          btn.textContent = 'Add to cart';
          btn.classList.remove('added');
        }, 1400);
      });
    });
  }

  function wireDetailPageCart(){
    document.querySelectorAll('button.normal').forEach(btn => {
      if(!btn.textContent.toLowerCase().includes('add to cart')) return;
      const detailContainer = btn.closest('.single-pro-details');
      if(!detailContainer) return;
      btn.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const price = getDetailPrice(detailContainer) || 0;
        const title = getDetailTitle(detailContainer);
        const qty = getDetailQty(detailContainer);
        const img = document.querySelector('.single-pro-image img')?.getAttribute('src') || '';
        const id = (title + '_' + img).replace(/\s+/g,'_').slice(0,120);
        addToCart({ id, title, price, qty, img });
        btn.textContent = 'Added to cart';
        btn.classList.add('added');
        setTimeout(() => {
          btn.textContent = 'Add to cart';
          btn.classList.remove('added');
        }, 1400);
      });
    });
  }

  // Render cart into Cart.html table
  function renderCartPage(){
    const tbody = document.querySelector('#cart-table tbody');
    if(!tbody) return;
    const cart = getCart();
    tbody.innerHTML = '';
    if(cart.length === 0){
      document.getElementById('cart-empty').style.display = 'block';
    } else {
      document.getElementById('cart-empty').style.display = 'none';
    }
    let total = 0;
    cart.forEach((item, idx)=>{
      const tr = document.createElement('tr');
      tr.className = 'cart-row';
      const subtotal = item.price * item.qty;
      total += subtotal;
      tr.innerHTML = `
        <td style="padding:12px;display:flex;gap:12px;align-items:center">
          <img src="${item.img}" alt="" style="width:80px;height:80px;object-fit:cover">
          <div>
            <div class="cart-title">${item.title}</div>
          </div>
        </td>
        <td style="text-align:center"><span class="cart-price">${item.price}</span></td>
        <td style="text-align:center"><input class="qty" type="number" min="1" value="${item.qty}" style="width:60px;padding:6px;border-radius:4px;border:1px solid #ccc"></td>
        <td style="text-align:center"><span class="cart-sub">${subtotal}</span></td>
        <td style="text-align:center"><button class="remove" data-idx="${idx}" style="background:transparent;border:0;color:#f44336;cursor:pointer">Remove</button></td>
      `;
      tbody.appendChild(tr);
    });
    const totEl = document.getElementById('total');
    const grandEl = document.getElementById('grand');
    if(totEl) totEl.textContent = total;
    if(grandEl) grandEl.textContent = total;
  }

  // wire cart interactions on Cart page
  function wireCartInteractions(){
    document.addEventListener('click', event=>{
      if (!(event.target instanceof Element)) return;
      const removeButton = event.target.closest('.remove');
      if (!removeButton) return;

      const idx = Number.parseInt(removeButton.getAttribute('data-idx'), 10);
      const cart = getCart();
      if (Number.isInteger(idx) && idx >= 0 && idx < cart.length) {
        cart.splice(idx, 1);
        saveCart(cart);
        renderCartPage();
      }
    });
    document.addEventListener('change', event=>{
      if (!(event.target instanceof HTMLInputElement) || !event.target.matches('.qty')) return;

      const row = event.target.closest('.cart-row');
      const tbody = row?.parentElement;
      if (!row || !tbody) return;

      const rows = Array.from(tbody.querySelectorAll('.cart-row'));
      const idx = rows.indexOf(row);
      const cart = getCart();
      const quantity = Number.parseInt(event.target.value, 10);
      const value = Number.isNaN(quantity) || quantity < 1 ? 1 : quantity;
      event.target.value = String(value);

      if (cart[idx]) {
        cart[idx].qty = value;
        saveCart(cart);
        renderCartPage();
      }
    });
  }

  // init
  document.addEventListener('DOMContentLoaded', ()=>{
    enhanceProducts();
    wireDetailPageCart();
    // if on cart page, render
    if(document.querySelector('#cart-table')){
      renderCartPage();
      wireCartInteractions();
    }
  });

})();
